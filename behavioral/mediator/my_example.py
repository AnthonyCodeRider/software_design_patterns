from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class EventManager(Protocol):
    """Mediator"""

    def notify(self, sender: object, event: Event) -> None: ...


@dataclass
class Event:
    name: str
    payload: dict | None = None


class Component:
    """Base Component. Knows only the mediator, never other components."""

    def __init__(self, mediator: EventManager | None = None):
        self._mediator = mediator

    def set_mediator(self, mediator: EventManager) -> None:
        self._mediator = mediator


# Concrete components


class SchemaService(Component):
    def add_column(self, name: str, data_type: str) -> None:
        print(f"SchemaService: adding column '{name}'")
        self._mediator.notify(self, Event("column_added", {"column_name": name, "data_type": data_type}))

    def remove_column(self, name: str) -> None:
        print(f"SchemaService: removing column '{name}'")
        self._mediator.notify(self, Event("column_removed", {"column_name": name}))

    def modify_column(self, name: str, new_data_type: str) -> None:
        print(f"SchemaService: modifying column '{name}'")
        self._mediator.notify(self, Event("column_modified", {"column_name": name, "new_data_type": new_data_type}))


class DataService(Component):
    def insert_row(self, row: dict) -> None:
        print(f"DataService: inserting row {row}")
        self._mediator.notify(self, Event("row_inserted", row))

    def update_row(self, row: dict) -> None:
        print(f"DataService: updating row {row}")
        self._mediator.notify(self, Event("row_updated", row))

    def delete_row(self, row_id: int) -> None:
        print(f"DataService: deleting row {row_id}")
        self._mediator.notify(self, Event("row_deleted", {"id": row_id}))


class MetadataStore(Component):
    def update(self, table_name: str, payload: dict | None) -> None:
        print(f"MetadataStore: updating metadata for '{table_name}' with {payload}")


class RowStore(Component):
    def backfill(self, table_name: str, payload: dict | None) -> None:
        print(f"RowStore: backfilling existing rows in '{table_name}' with {payload}")
        self._mediator.notify(self, Event("backfill_done", payload))

    def remove_column(self, table_name: str, payload: dict | None) -> None:
        print(f"RowStore: removing column from existing rows in '{table_name}' with {payload}")

    def modify_column(self, table_name: str, payload: dict | None) -> None:
        print(f"RowStore: modifying column in existing rows in '{table_name}' with {payload}")

    def process_new_row(self, table_name: str, payload: dict | None) -> None:
        print(f"RowStore: processing new row in '{table_name}' with {payload}")

    def process_updated_row(self, table_name: str, payload: dict | None) -> None:
        print(f"RowStore: processing updated row in '{table_name}' with {payload}")

    def process_deleted_row(self, table_name: str, payload: dict | None) -> None:
        print(f"RowStore: processing deleted row in '{table_name}' with {payload}")


class SchemaEventsManager:
    """Concrete Mediator. Coordinates schema changes using MetadataStore and RowStore."""

    def __init__(self, table_name: str, schema: SchemaService, metadata: MetadataStore, rows: RowStore):
        self._table_name = table_name
        self._schema = schema
        self._metadata = metadata
        self._rows = rows

        for component in (schema, metadata, rows):
            component.set_mediator(self)

    def notify(self, sender: object, event: Event) -> None:
        print(f"SchemaEventsManager: '{event.name}' from {type(sender).__name__}")
        match event.name:
            case "column_added":
                self._metadata.update(self._table_name, event.payload)
                self._rows.backfill(self._table_name, event.payload)
            case "column_removed":
                self._metadata.update(self._table_name, event.payload)
                self._rows.remove_column(self._table_name, event.payload)
            case "column_modified":
                self._metadata.update(self._table_name, event.payload)
                self._rows.modify_column(self._table_name, event.payload)
            case "backfill_done":
                print(f"SchemaEventsManager: backfill finished for '{self._table_name}'")
            case _:
                print(f"SchemaEventsManager: no action defined for '{event.name}'")


class DataEventsManager:
    """Concrete Mediator. Coordinates row changes using the same MetadataStore and RowStore classes."""

    def __init__(self, table_name: str, data: DataService, metadata: MetadataStore, rows: RowStore):
        self._table_name = table_name
        self._data = data
        self._metadata = metadata
        self._rows = rows

        for component in (data, metadata, rows):
            component.set_mediator(self)

    def notify(self, sender: object, event: Event) -> None:
        print(f"DataEventsManager: '{event.name}' from {type(sender).__name__}")
        match event.name:
            case "row_inserted":
                self._metadata.update(self._table_name, event.payload)
                self._rows.process_new_row(self._table_name, event.payload)
            case "row_updated":
                self._metadata.update(self._table_name, event.payload)
                self._rows.process_updated_row(self._table_name, event.payload)
            case "row_deleted":
                self._metadata.update(self._table_name, event.payload)
                self._rows.process_deleted_row(self._table_name, event.payload)
            case _:
                print(f"DataEventsManager: no action defined for '{event.name}'")


if __name__ == "__main__":
    # Both mediators use the same component classes and coordinate them differently.
    # Each mediator gets its own instances because a component reports to exactly one mediator.
    schema = SchemaService()
    SchemaEventsManager("users", schema, MetadataStore(), RowStore())

    data = DataService()
    DataEventsManager("users", data, MetadataStore(), RowStore())

    # The client works with components. Components talk only to their mediator.
    schema.add_column("age", "int")
    schema.remove_column("address")
    schema.modify_column("email", "varchar(255)")
    data.insert_row({"id": 1, "name": "Alice"})
    data.update_row({"id": 1, "name": "Alice Smith"})
    data.delete_row(1)
