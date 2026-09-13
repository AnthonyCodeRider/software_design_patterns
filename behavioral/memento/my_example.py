"""Zero-copy clone before a full refresh."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import uuid4


class Originator(Protocol):
    def save(self) -> Memento: ...

    def restore(self, memento: Memento) -> None: ...


class Memento(Protocol):
    def get_state(self) -> str: ...

    def get_name(self) -> str: ...

    def get_date(self) -> str: ...


class Caretaker(Protocol):
    def backup(self) -> None: ...

    def undo(self) -> None: ...

    def show_history(self) -> None: ...


class Warehouse(Protocol):
    def overwrite(self, table_name: str, data: str) -> None: ...

    def clone(self, table_name: str, clone_id: str) -> None: ...

    def swap(self, table_name: str, clone_id: str) -> None: ...


class BQWarehouse:
    def overwrite(self, table_name: str, data: str) -> None:
        print(f"BQWarehouse: INSERT OVERWRITE {table_name} with {data}")

    def clone(self, table_name: str, clone_id: str) -> None:
        print(f"BQWarehouse: CREATE TABLE {clone_id} CLONE {table_name} (metadata-only)")

    def swap(self, table_name: str, clone_id: str) -> None:
        print(f"BQWarehouse: SWAP {table_name} <- {clone_id}")


class ManagedTable:
    """Originator"""

    def __init__(self, table_name: str, warehouse: Warehouse) -> None:
        self.table_name = table_name
        self._warehouse = warehouse
        # No _state field: the rows this originator is responsible for live in the warehouse, not in the process.
        # That is exactly why the memento can only be a reference.

    def save(self) -> TableSnapshot:
        """Cheap: the clone is metadata-only and the memento holds just its id."""
        taken_at = datetime.now()
        clone_id = f"{self.table_name}-bak-{taken_at:%Y%m%d%H%M%S}-{uuid4().hex[:8]}"
        self._warehouse.clone(self.table_name, clone_id)
        return TableSnapshot(clone_id, taken_at)

    def restore(self, memento: Memento) -> None:
        self._warehouse.swap(self.table_name, memento.get_state())

    def insert_overwrite(self, data: str) -> None:
        """Business logic, destructive. Back up before calling this."""
        self._warehouse.overwrite(self.table_name, data)


class TableSnapshot:
    """Memento"""

    def __init__(self, clone_id: str, taken_at: datetime) -> None:
        self._clone_id = clone_id
        self._taken_at = taken_at

    def get_state(self) -> str:
        return self._clone_id

    def get_date(self) -> str:
        return f"{self._taken_at:%Y-%m-%d %H:%M:%S}"

    def get_name(self) -> str:
        return f"clone_id={self._clone_id} date={self.get_date()}"


class TableManager:
    """Caretaker"""

    def __init__(self, managed_table: Originator) -> None:
        self._mementos: list[Memento] = []
        self._managed_table = managed_table

    def backup(self) -> None:
        print("TableManager: Saving ManagedTable's state...")
        self._mementos.append(self._managed_table.save())

    def undo(self) -> None:
        if not self._mementos:
            print("TableManager: no snapshots left to roll back to.")
            return

        memento = self._mementos[-1]
        print(f"TableManager: restoring state to: {memento.get_name()}")
        self._managed_table.restore(memento)
        self._mementos.pop()

    def show_history(self) -> None:
        print("TableManager: Here's the list of mementos:")
        for memento in self._mementos:
            print(memento.get_name())


if __name__ == "__main__":
    warehouse: Warehouse = BQWarehouse()
    managed_table = ManagedTable("my_table", warehouse)
    table_manager: Caretaker = TableManager(managed_table)

    table_manager.backup()
    managed_table.insert_overwrite("New data 1")

    table_manager.backup()
    managed_table.insert_overwrite("New data 2")

    table_manager.show_history()

    print("Rolling back...")
    table_manager.undo()

    print("Rolling back again...")
    table_manager.undo()

    table_manager.show_history()
