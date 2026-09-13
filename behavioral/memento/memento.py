from __future__ import annotations

import http
import random
from abc import ABC, abstractmethod
from datetime import datetime


class Originator:
    """
    The Originator class holds some important state that may change over time.
    It also defines a method for saving the state inside a memento and another method for restoring the state from a memento.
    """

    _state = None  # For simplicity, the state is stored as a single string.

    def __init__(self, state: str) -> None:
        self._state = state
        print(f"Originator: My initial state is: {self._state}")

    def do_something(self) -> None:
        """
        The Originator's business logic may affect its internal state.
        Therefore, the client should backup the state before launching methods of the business logic via the save method.
        """
        print("Originator: I'm doing something important...")
        self._state = random.choice(list(http.HTTPStatus)).phrase

    def save(self) -> Memento:
        """Saves the current state inside a memento."""
        print("Originator: Saving to Memento.")
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento) -> None:
        """Restores the Originator's state from a memento object."""
        self._state = memento.get_state()
        print(f"Originator: My state has changed to: {self._state}")


class Memento(ABC):
    """
    The Memento interface provides a way to retrieve the memento's metadata, such as creation date or name.
    However, it doesn't expose the Originator's state.
    """

    @abstractmethod
    def get_name(self) -> str: ...

    @abstractmethod
    def get_date(self) -> str: ...


class ConcreteMemento(Memento):
    def __init__(self, state: str) -> None:
        self._state = state
        self._date = datetime.now().strftime("%Y-%m-%d %H:%M")

    def get_state(self) -> str:
        """The Originator uses this method when restoring its state."""
        return self._state

    def get_name(self) -> str:
        """The rest of the methods are used by the Caretaker to display metadata."""
        return f"state={self._state} date={self._date}"

    def get_date(self) -> str:
        return self._date


class Caretaker:
    """
    The Caretaker doesn't depend on the Concrete Memento class.
    Therefore, it doesn't have access to the originator's state, stored inside the memento.
    It works with all mementos via the base interface.
    """

    def __init__(self, originator: Originator) -> None:
        self._mementos = []
        self._originator = originator

    def backup(self) -> None:
        print("Caretaker: Saving Originator's state...")
        self._mementos.append(self._originator.save())

    def undo(self) -> None:
        if not self._mementos:
            return

        memento = self._mementos.pop()
        print(f"Caretaker: restoring state to: {memento.get_name()}")
        try:
            self._originator.restore(memento)
        except Exception:
            self.undo()

    def show_history(self) -> None:
        print("Caretaker: Here's the list of mementos:")
        for memento in self._mementos:
            print(memento.get_name())


if __name__ == "__main__":
    originator = Originator("Not Found")
    caretaker = Caretaker(originator)

    caretaker.backup()
    originator.do_something()

    caretaker.backup()
    originator.do_something()

    caretaker.backup()
    originator.do_something()

    caretaker.show_history()

    print("Client: now, let's rollback!")
    caretaker.undo()

    print("Client: once more!")
    caretaker.undo()
