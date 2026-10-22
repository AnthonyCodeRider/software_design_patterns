"""Behavior that every refactor must keep.

By default the tests run against kata.py. To run them against another module:

    KATA_MODULE=solution_pythonic uv run --with pytest pytest
"""

import importlib
import os

import pytest

kata = importlib.import_module(os.environ.get("KATA_MODULE", "kata"))

S3_ORDERS = "s3://landing/orders/"
S3_DEVICES = "s3://landing/devices/"
BQ_ORDERS = "dpe.raw.orders"
BQ_CLICKS = "dpe.raw.clicks"


@pytest.fixture(autouse=True)
def cloud():
    kata.CLOUD.reset()
    return kata.CLOUD


def test_json_order_drops_pii_and_adds_ingested_at(cloud):
    rows = kata.process_message("orders", '{"order_id": 1, "amount": 9.5, "email": "a@b.nl"}')

    assert len(rows) == 1
    assert rows[0]["order_id"] == 1
    assert rows[0]["amount"] == 9.5
    assert "email" not in rows[0]
    assert "ingested_at" in rows[0]
    assert '"order_id": 1' in cloud.s3[S3_ORDERS][0]


def test_orders_go_to_s3_and_bigquery(cloud):
    kata.process_message("orders", '{"order_id": 1, "amount": 2}')

    assert len(cloud.s3[S3_ORDERS]) == 1
    assert cloud.bigquery[BQ_ORDERS][0][0]["order_id"] == "1"


def test_json_list_is_written_in_batches(cloud):
    raw = '[{"order_id": 1, "amount": 1}, {"order_id": 2, "amount": 2}, {"order_id": 3, "amount": 3}]'

    rows = kata.process_message("orders", raw)

    assert [row["order_id"] for row in rows] == [1, 2, 3]
    assert len(cloud.s3[S3_ORDERS]) == 2
    assert cloud.s3[S3_ORDERS][0].count("\n") == 1
    assert cloud.s3[S3_ORDERS][1].count("\n") == 0


def test_csv_clicks_go_to_bigquery_only(cloud):
    rows = kata.process_message("clicks", "user_id,url,email\n42,/cart,a@b.nl\n")

    assert rows[0]["user_id"] == "42"
    assert "email" not in rows[0]
    assert cloud.bigquery[BQ_CLICKS][0][0]["url"] == "/cart"
    assert cloud.s3 == {}


def test_kv_devices_go_to_s3_only(cloud):
    rows = kata.process_message("devices", "device_id=d-7; firmware=1.2; phone=0612345678")

    assert rows[0]["device_id"] == "d-7"
    assert rows[0]["firmware"] == "1.2"
    assert "phone" not in rows[0]
    assert len(cloud.s3[S3_DEVICES]) == 1
    assert cloud.bigquery == {}


def test_missing_required_field_writes_nothing(cloud):
    with pytest.raises(kata.ValidationError):
        kata.process_message("orders", '[{"order_id": 1, "amount": 2}, {"order_id": 2}]')

    assert cloud.s3 == {}
    assert cloud.bigquery == {}


def test_unknown_topic_is_rejected():
    with pytest.raises(ValueError):
        kata.process_message("payments", "{}")


def test_transient_sink_failure_is_retried(cloud):
    cloud.outages["s3"] = 2

    kata.process_message("orders", '{"order_id": 1, "amount": 2}')

    assert cloud.connect_attempts["s3"] == 3
    assert len(cloud.s3[S3_ORDERS]) == 1


def test_permanent_sink_failure_gives_up_after_three_attempts(cloud):
    cloud.outages["bigquery"] = 3

    with pytest.raises(ConnectionError):
        kata.process_message("clicks", "user_id,url\n42,/cart\n")

    assert cloud.connect_attempts["bigquery"] == 3
    assert cloud.bigquery == {}
