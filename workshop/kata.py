from __future__ import annotations

import csv
import io
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

TOPIC_CONFIG: dict[str, dict[str, Any]] = {
    "orders": {"format": "json", "required": ["order_id", "amount"], "sinks": ["s3", "bigquery"]},
    "clicks": {"format": "csv", "required": ["user_id", "url"], "sinks": ["bigquery"]},
    "devices": {"format": "kv", "required": ["device_id"], "sinks": ["s3"]},
}

PII_FIELDS = ("email", "phone")
BATCH_SIZE = 2
MAX_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 0.01


class ValidationError(ValueError):
    pass


class FakeCloud:
    """Not part of the refactor"""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.s3: dict[str, list[str]] = {}
        self.bigquery: dict[str, list[list[dict[str, Any]]]] = {}
        self.outages = {"s3": 0, "bigquery": 0}
        self.connect_attempts = {"s3": 0, "bigquery": 0}

    def connect(self, service: str) -> None:
        self.connect_attempts[service] += 1
        if self.outages[service] > 0:
            self.outages[service] -= 1
            raise ConnectionError(f"{service}: connection refused")


CLOUD = FakeCloud()


class S3Sink:
    def __init__(self, bucket: str, prefix: str) -> None:
        self.path = f"s3://{bucket}/{prefix}/"
        self._connected = False

    def write_to_s3(self, rows: list[dict[str, Any]]) -> None:
        # open
        CLOUD.connect("s3")
        self._connected = True
        logger.info("S3: connected, writing to %s", self.path)

        # write in batches
        for i in range(0, len(rows), BATCH_SIZE):
            batch = rows[i : i + BATCH_SIZE]
            body = "\n".join(json.dumps(row, sort_keys=True) for row in batch)
            CLOUD.s3.setdefault(self.path, []).append(body)
            logger.info("S3: uploaded %d rows", len(batch))

        # close
        self._connected = False
        logger.info("S3: connection closed")


class BigQuerySink:
    def __init__(self, project: str, dataset: str, table: str) -> None:
        self.table_id = f"{project}.{dataset}.{table}"
        self._client = None

    def insert_rows(self, rows: list[dict[str, Any]]) -> None:
        # connect
        CLOUD.connect("bigquery")
        self._client = object()
        logger.info("BigQuery: connected, inserting into %s", self.table_id)

        # insert in batches
        for i in range(0, len(rows), BATCH_SIZE):
            batch = rows[i : i + BATCH_SIZE]
            payload = [{k: str(v) for k, v in row.items()} for row in batch]
            CLOUD.bigquery.setdefault(self.table_id, []).append(payload)
            logger.info("BigQuery: inserted %d rows", len(batch))

        # disconnect
        self._client = None
        logger.info("BigQuery: client closed")


def process_message(topic: str, raw: str) -> list[dict[str, Any]]:
    config = TOPIC_CONFIG.get(topic)
    if config is None:
        raise ValueError(f"Unknown topic: {topic}")

    # parse
    if config["format"] == "json":
        data = json.loads(raw)
        rows = data if isinstance(data, list) else [data]
    elif config["format"] == "csv":
        reader = csv.DictReader(io.StringIO(raw.strip()))
        rows = [dict(row) for row in reader]
    elif config["format"] == "kv":
        rows = []
        for line in raw.strip().splitlines():
            row = {}
            for pair in line.split(";"):
                key, _, value = pair.partition("=")
                row[key.strip()] = value.strip()
            rows.append(row)
    else:
        raise ValueError(f"Unknown format: {config['format']}")

    # clean
    result = []
    for row in rows:
        missing = [field for field in config["required"] if row.get(field) in (None, "")]
        if missing:
            raise ValidationError(f"{topic}: missing required fields {missing}")
        for field in PII_FIELDS:
            row.pop(field, None)
        row["ingested_at"] = datetime.now(timezone.utc).isoformat()
        result.append(row)

    # write
    for sink_name in config["sinks"]:
        if sink_name == "s3":
            s3 = S3Sink(bucket="landing", prefix=topic)
            for attempt in range(1, MAX_ATTEMPTS + 1):
                start = time.perf_counter()
                try:
                    s3.write_to_s3(result)
                    break
                except ConnectionError as error:
                    logger.warning("S3 write failed (attempt %d/%d): %s", attempt, MAX_ATTEMPTS, error)
                    if attempt == MAX_ATTEMPTS:
                        raise
                    time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                finally:
                    logger.info("S3 write took %.3fs", time.perf_counter() - start)
        elif sink_name == "bigquery":
            bq = BigQuerySink(project="dpe", dataset="raw", table=topic)
            for attempt in range(1, MAX_ATTEMPTS + 1):
                start = time.perf_counter()
                try:
                    bq.insert_rows(result)
                    break
                except ConnectionError as error:
                    logger.warning("BigQuery write failed (attempt %d/%d): %s", attempt, MAX_ATTEMPTS, error)
                    if attempt == MAX_ATTEMPTS:
                        raise
                    time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                finally:
                    logger.info("BigQuery write took %.3fs", time.perf_counter() - start)
        else:
            raise ValueError(f"Unknown sink: {sink_name}")

    return result
