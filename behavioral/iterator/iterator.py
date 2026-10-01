"""
In python there are 2 abstract classes from the built-in collections module:
    - Iterable (__iter__ method has to be implemented)
    - Iterator (__next__ method has to be implemented)
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any


class AlphabeticalOrderIterator(Iterator):
    """
    Concrete Iterators implement various traversal algorithms.
    These classes store the current traversal position at all times.
    """

    _position: int = None  # current traversal position
    # Iterator may have a lot of other fields to store the iteration state, especially when it is a complex algorithm.

    _reverse: bool = False  # indicates the traversal direction

    def __init__(self, collection: WordsCollection, reverse: bool = False) -> None:
        self._collection = collection
        self._reverse = reverse
        self._position = 0
        self._sorted_items = None  # will be set on the first call to __next__ (lazy initialization)

    def __next__(self) -> Any:
        """
        Returns the next item in the sequence.
        If there are no further items, StopIteration is raised.
        """
        # Sorting happens only on the first call to __next__ (lazy initialization)
        if self._sorted_items is None:
            self._sorted_items = sorted(self._collection._collection)
            if self._reverse:
                self._sorted_items.reverse()

        if self._position >= len(self._sorted_items):
            raise StopIteration()

        value = self._sorted_items[self._position]
        self._position += 1
        return value


class WordsCollection(Iterable):
    """Concrete Collections provide one or several methods for retrieving fresh iterator instances, compatible with the collection class."""

    def __init__(self, collection: list[Any] | None = None) -> None:
        self._collection = collection or []

    def __getitem__(self, index: int) -> Any:
        return self._collection[index]

    def __iter__(self) -> AlphabeticalOrderIterator:
        """
        The __iter__ method returns the iterator object itself.

        In this case, it returns the iterator in the ascending order by default.
        """
        return AlphabeticalOrderIterator(self)

    def get_reverse_iterator(self) -> AlphabeticalOrderIterator:
        return AlphabeticalOrderIterator(self, True)

    def add_item(self, item: Any) -> None:
        self._collection.append(item)


if __name__ == "__main__":
    # The client code may or may not know about the concrete collection or iterator classes.
    # Depending on the level of indirection you want to keep in your program.
    collection = WordsCollection()
    collection.add_item("B")
    collection.add_item("A")
    collection.add_item("C")

    print("Straight traversal:")
    print(",".join(collection))

    print("Reverse traversal:")
    print(",".join(collection.get_reverse_iterator()))
