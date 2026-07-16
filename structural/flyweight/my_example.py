from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductInfo:
    """Shared (intrinsic) state: identical for every order line of the same product, cached once and reused."""

    product_id: str
    name: str
    category: str
    unit_price: float


@dataclass
class OrderLineFact:
    """Unique (extrinsic) state per row, holding just a reference to the shared ProductInfo flyweight."""

    order_id: str
    timestamp: str
    quantity: int
    product: ProductInfo

    def __str__(self):
        return f"OrderLineFact(order_id={self.order_id}, product_id={self.product.product_id})"


class ProductInfoFactory:
    """Caches ProductInfo flyweights by product_id so catalog data is never loaded twice."""

    def __init__(self):
        self._cache: dict[str, ProductInfo] = {}

    def get_product_info(self, product_id, name, category, unit_price) -> ProductInfo:
        if product_id not in self._cache:
            print(f"ProductInfoFactory: loading product {product_id} from the catalog.")
            self._cache[product_id] = ProductInfo(product_id, name, category, unit_price)
        else:
            print(f"ProductInfoFactory: reusing cached product {product_id}.")
        return self._cache[product_id]

    def cached_count(self) -> int:
        return len(self._cache)


def ingest_order_line(factory: ProductInfoFactory, raw_row: dict) -> OrderLineFact:
    """Simulates ingesting one row of a huge orders dataset, reusing a shared ProductInfo instead of allocating a new one per row."""
    product = factory.get_product_info(raw_row["product_id"], raw_row["product_name"], raw_row["category"], raw_row["unit_price"])
    return OrderLineFact(raw_row["order_id"], raw_row["timestamp"], raw_row["quantity"], product)


if __name__ == "__main__":
    raw_rows = [
        {
            "order_id": "O1001",
            "timestamp": "2026-07-14T10:00",
            "quantity": 2,
            "product_id": "P1",
            "product_name": "Wireless Mouse",
            "category": "Electronics",
            "unit_price": 25.0,
        },
        {
            "order_id": "O1002",
            "timestamp": "2026-07-14T10:05",
            "quantity": 1,
            "product_id": "P2",
            "product_name": "USB-C Cable",
            "category": "Electronics",
            "unit_price": 9.0,
        },
        {
            "order_id": "O1003",
            "timestamp": "2026-07-14T10:07",
            "quantity": 5,
            "product_id": "P1",
            "product_name": "Wireless Mouse",
            "category": "Electronics",
            "unit_price": 25.0,
        },
        {
            "order_id": "O1004",
            "timestamp": "2026-07-14T10:12",
            "quantity": 3,
            "product_id": "P1",
            "product_name": "Wireless Mouse",
            "category": "Electronics",
            "unit_price": 25.0,
        },
    ]

    factory = ProductInfoFactory()
    facts = [ingest_order_line(factory, row) for row in raw_rows]

    for fact in facts:
        print(fact)

    print(f"\n{len(facts)} order lines ingested, only {factory.cached_count()} distinct ProductInfo objects in memory.")

