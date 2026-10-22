from __future__ import annotations

import csv
import functools
import io
import json
import logging
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from kata import CLOUD, FakeCloud  # noqa: F401  (the fake cloud is not part of the refactor)

logger = logging.getLogger(__name__)

Row = dict[str, Any]
Parser = Callable[[str], list[Row]]

PII_FIELDS = ("email", "phone")
BATCH_SIZE = 2
MAX_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 0.01


class ValidationError(ValueError):
    pass


# Strategy: a parser is any function from raw text to rows


def parse_json(raw: str) -> list[Row]:
    data = json.loads(raw)
    return data if isinstance(data, list) else [data]


def parse_csv(raw: str) -> list[Row]:
    return [dict(row) for row in csv.DictReader(io.StringIO(raw.strip()))]


def parse_kv(raw: str) -> list[Row]:
    return [{key.strip(): value.strip() for key, _, value in (pair.partition("=") for pair in line.split(";"))} for line in raw.strip().splitlines()]


# Decorator: plain Python decorators add retry and timing to any function


def retry(attempts: int) -> Callable[[Callable[..., None]], Callable[..., None]]:
    def decorator(func: Callable[..., None]) -> Callable[..., None]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> None:
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except ConnectionError as error:
                    logger.warning("%s failed (attempt %d/%d): %s", func.__name__, attempt, attempts, error)
                    if attempt == attempts:
                        raise
                    time.sleep(RETRY_BACKOFF_SECONDS * attempt)

        return wrapper

    return decorator


def timed(func: Callable[..., None]) -> Callable[..., None]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            logger.info("%s took %.3fs", func.__name__, time.perf_counter() - start)

    return wrapper


# Template Method: the one place a base class earns its keep


class Sink(ABC):
    service: str

    @timed
    @retry(attempts=MAX_ATTEMPTS)
    def write(self, rows: list[Row]) -> None:
        CLOUD.connect(self.service)
        for i in range(0, len(rows), BATCH_SIZE):
            self.send(self.serialize(rows[i : i + BATCH_SIZE]))
        logger.info("%s: wrote %d rows", self.service, len(rows))

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


# Factory: a dict from sink name to a function that builds the sink for a topic


SINK_FACTORIES: dict[str, Callable[[str], Sink]] = {
    "s3": functools.partial(S3Sink, "landing"),
    "bigquery": functools.partial(BigQuerySink, "dpe", "raw"),
}


# Wiring


@dataclass(frozen=True)
class Topic:
    parse: Parser
    required: tuple[str, ...]
    sinks: tuple[str, ...]


TOPICS = {
    "orders": Topic(parse_json, ("order_id", "amount"), ("s3", "bigquery")),
    "clicks": Topic(parse_csv, ("user_id", "url"), ("bigquery",)),
    "devices": Topic(parse_kv, ("device_id",), ("s3",)),
}


def clean(row: Row, required: tuple[str, ...]) -> Row:
    missing = [field for field in required if row.get(field) in (None, "")]
    if missing:
        raise ValidationError(f"missing required fields {missing}")
    cleaned = {key: value for key, value in row.items() if key not in PII_FIELDS}
    return {**cleaned, "ingested_at": datetime.now(timezone.utc).isoformat()}


def process_message(topic: str, raw: str) -> list[Row]:
    if topic not in TOPICS:
        raise ValueError(f"Unknown topic: {topic}")
    config = TOPICS[topic]

    rows = [clean(row, config.required) for row in config.parse(raw)]

    for name in config.sinks:
        SINK_FACTORIES[name](topic).write(rows)

    return rows
