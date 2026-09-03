from __future__ import annotations

from abc import ABC, abstractmethod


class Subject(ABC):
    """The Subject (Publisher) interface declares a set of methods for managing subscribers."""

    @abstractmethod
    def attach(self, observer: Observer):
        """Attach an observer to the subject."""
        pass

    @abstractmethod
    def detach(self, observer: Observer):
        """Detach an observer from the subject."""
        pass

    @abstractmethod
    def notify(self):
        """Notify all observers about an event."""
        pass


class ConcreteSubject(Subject):
    """The ConcreteSubject owns some important state and notifies observers when the state changes."""

    _state: int = None  # For the sake of simplicity, the Subject's state, essential to all subscribers, is stored in this variable.
    # List of subscribers. In real life, the list of subscribers can be stored more comprehensively (categorized by event type, etc.).
    _observers: list[Observer] = []

    def attach(self, observer: Observer):
        """Attach an observer to the subject."""
        self._observers.append(observer)

    def detach(self, observer: Observer):
        """Detach an observer from the subject."""
        self._observers.remove(observer)

    def notify(self):
        """Notify all observers about an event."""
        for observer in self._observers:
            observer.update(self)

    def some_business_logic(self):
        """Some business logic that changes the state of the subject."""
        print("\nSubject: I'm doing something important.")
        self._state = 42  # The state has changed.
        print(f"Subject: My state has just changed to: {self._state}")
        self.notify()  # Notify all observers about the state change.


class Observer(ABC):
    """The Observer interface declares the update method, used by subjects."""

    @abstractmethod
    def update(self, subject: Subject):
        """Receive update from subject."""
        pass


class ConcreteObserverA(Observer):
    """Concrete Observers react to the updates issued by the Subject they had been attached to."""

    def update(self, subject: Subject):
        if subject._state < 3:
            print("ConcreteObserverA: Reacted to the event.")


class ConcreteObserverB(Observer):
    """Concrete Observers react to the updates issued by the Subject they had been attached to."""

    def update(self, subject: Subject):
        if subject._state == 0 or subject._state >= 2:
            print("ConcreteObserverB: Reacted to the event.")


if __name__ == "__main__":
    # The client code.

    subject = ConcreteSubject()

    observer_a = ConcreteObserverA()
    subject.attach(observer_a)

    observer_b = ConcreteObserverB()
    subject.attach(observer_b)

    subject.some_business_logic()
    subject.some_business_logic()

    subject.detach(observer_a)

    subject.some_business_logic()
