from __future__ import annotations

import csv
import io
import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Protocol

from kata import CLOUD, FakeCloud  # noqa: F401  (the fake cloud is not part of the refactor)

logger = logging.getLogger(__name__)

Row = dict[str, Any]

PII_FIELDS = ("email", "phone")
BATCH_SIZE = 2
MAX_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 0.01


class ValidationError(ValueError):
    pass


# Strategy: one parser class per message format


class Parser(Protocol):
    def parse(self, raw: str) -> list[Row]: ...


class JsonParser:
    def parse(self, raw: str) -> list[Row]:
        data = json.loads(raw)
        return data if isinstance(data, list) else [data]


class CsvParser:
    def parse(self, raw: str) -> list[Row]:
        return [dict(row) for row in csv.DictReader(io.StringIO(raw.strip()))]


class KeyValueParser:
    def parse(self, raw: str) -> list[Row]:
        rows = []
        for line in raw.strip().splitlines():
            row = {}
            for pair in line.split(";"):
                key, _, value = pair.partition("=")
                row[key.strip()] = value.strip()
            rows.append(row)
        return rows


# Template Method: Sink.write() fixes the steps, subclasses fill in the details


class Writer(Protocol):
    def write(self, rows: list[Row]) -> None: ...


class Sink(ABC):
    service: str

    def write(self, rows: list[Row]) -> None:
        self.open()
        for i in range(0, len(rows), BATCH_SIZE):
            batch = rows[i : i + BATCH_SIZE]
            self.send(self.serialize(batch))
            logger.info("%s: wrote %d rows", self.service, len(batch))
        self.close()

    def open(self) -> None:
        CLOUD.connect(self.service)
        logger.info("%s: connected", self.service)

    def close(self) -> None:
        logger.info("%s: connection closed", self.service)

    @abstractmethod
    def serialize(self, batch: list[Row]) -> Any: ...

    @abstractmethod
    def send(self, payload: Any) -> None: ...


class S3Sink(Sink):
    service = "s3"

    def __init__(self, bucket: str, prefix: str) -> None:
        self.path = f"s3://{bucket}/{prefix}/"

    def serialize(self, batch: list[Row]) -> str:
        return "\n".join(json.dumps(row, sort_keys=True) for row in batch)

    def send(self, payload: str) -> None:
        CLOUD.s3.setdefault(self.path, []).append(payload)


class BigQuerySink(Sink):
    service = "bigquery"

    def __init__(self, project: str, dataset: str, table: str) -> None:
        self.table_id = f"{project}.{dataset}.{table}"

    def serialize(self, batch: list[Row]) -> list[Row]:
        return [{k: str(v) for k, v in row.items()} for row in batch]

    def send(self, payload: list[Row]) -> None:
        CLOUD.bigquery.setdefault(self.table_id, []).append(payload)


# Factory: one creator per sink type knows how to build and configure it


class SinkFactory(ABC):
    @abstractmethod
    def create(self, topic: str) -> Sink: ...


class S3SinkFactory(SinkFactory):
    def create(self, topic: str) -> Sink:
        return S3Sink(bucket="landing", prefix=topic)


class BigQuerySinkFactory(SinkFactory):
    def create(self, topic: str) -> Sink:
        return BigQuerySink(project="dpe", dataset="raw", table=topic)


# Decorator: wrappers with the same write() interface add retry and timing


class WriterDecorator:
    def __init__(self, wrapped: Writer) -> None:
        self._wrapped = wrapped

    def write(self, rows: list[Row]) -> None:
        self._wrapped.write(rows)


class RetryingWriter(WriterDecorator):
    def write(self, rows: list[Row]) -> None:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                super().write(rows)
                return
            except ConnectionError as error:
                logger.warning("Write failed (attempt %d/%d): %s", attempt, MAX_ATTEMPTS, error)
                if attempt == MAX_ATTEMPTS:
                    raise
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)


class TimedWriter(WriterDecorator):
    def write(self, rows: list[Row]) -> None:
        start = time.perf_counter()
        try:
            super().write(rows)
        finally:
            logger.info("Write took %.3fs", time.perf_counter() - start)


# Wiring


class TopicConfig:
    def __init__(self, parser: Parser, required: list[str], sinks: list[SinkFactory]) -> None:
        self.parser = parser
        self.required = required
        self.sinks = sinks


TOPIC_CONFIG: dict[str, TopicConfig] = {
    "orders": TopicConfig(JsonParser(), ["order_id", "amount"], [S3SinkFactory(), BigQuerySinkFactory()]),
    "clicks": TopicConfig(CsvParser(), ["user_id", "url"], [BigQuerySinkFactory()]),
    "devices": TopicConfig(KeyValueParser(), ["device_id"], [S3SinkFactory()]),
}


def clean(topic: str, row: Row, required: list[str]) -> Row:
    missing = [field for field in required if row.get(field) in (None, "")]
    if missing:
        raise ValidationError(f"{topic}: missing required fields {missing}")
    for field in PII_FIELDS:
        row.pop(field, None)
    row["ingested_at"] = datetime.now(timezone.utc).isoformat()
    return row


def process_message(topic: str, raw: str) -> list[Row]:
    config = TOPIC_CONFIG.get(topic)
    if config is None:
        raise ValueError(f"Unknown topic: {topic}")

    rows = [clean(topic, row, config.required) for row in config.parser.parse(raw)]

    for factory in config.sinks:
        TimedWriter(RetryingWriter(factory.create(topic))).write(rows)

    return rows
