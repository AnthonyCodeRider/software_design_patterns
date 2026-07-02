from __future__ import annotations

from abc import ABC, abstractmethod


class Abstration:
    """Abstraction class defines the control interface and maintains a reference to an object of type Implementation."""

    def __init__(self, implementation: Implementation) -> None:
        self.implementation = implementation

    def do_operation(self):
        return self.implementation.do_operation()


class ExtendedAbstraction(Abstration):
    """Abstraction can be extended without changing the Implementation classes."""

    def do_operation(self):
        return f"ExtendedAbstraction: {self.implementation.do_operation()}"


class Implementation(ABC):
    """Defines an interface for implementation classes."""

    @abstractmethod
    def do_operation(self):
        pass


class ConcreteImplementationA(Implementation):
    def do_operation(self):
        return "ConcreteImplementationA: Operation performed."


class ConcreteImplementationB(Implementation):
    def do_operation(self):
        return "ConcreteImplementationB: Operation performed."


def client_code(abstraction: Abstration) -> None:
    """Client code works with an abstraction and can use any implementation."""

    print(abstraction.do_operation())


if __name__ == "__main__":
    implementation = ConcreteImplementationA()
    abstraction = Abstration(implementation)
    client_code(abstraction)

    implementation = ConcreteImplementationB()
    abstraction = ExtendedAbstraction(implementation)
    client_code(abstraction)
