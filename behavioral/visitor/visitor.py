from __future__ import annotations

from abc import ABC, abstractmethod


class Component(ABC):
    """Component interface declares an accept method that should take the base visitor interface as an argument."""

    @abstractmethod
    def accept(self, visitor: Visitor): ...


class Visitor(ABC):
    """
    Visitor interface declares a set of visiting methods that correspond to component classes.
    The signature of a visiting method allows the visitor to identify the exact class of the component that it's dealing with.
    """

    @abstractmethod
    def visit_concrete_component_a(self, element: ConcreteComponentA): ...

    @abstractmethod
    def visit_concrete_component_b(self, element: ConcreteComponentB): ...


class ConcreteComponentA(Component):
    """Concrete Components must implement the accept method in such a way that it calls the visitor's method corresponding to the component's class."""

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_concrete_component_a(self)

    def exclusive_method_of_concrete_component_a(self) -> str:
        return "A"


class ConcreteComponentB(Component):
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_concrete_component_b(self)

    def exclusive_method_of_concrete_component_b(self) -> str:
        return "B"


class ConcreteVisitor1(Visitor):
    def visit_concrete_component_a(self, element: ConcreteComponentA) -> None:
        result = element.exclusive_method_of_concrete_component_a()
        print(f"ConcreteVisitor1: {result}")

    def visit_concrete_component_b(self, element: ConcreteComponentB) -> None:
        result = element.exclusive_method_of_concrete_component_b()
        print(f"ConcreteVisitor1: {result}")


class ConcreteVisitor2(Visitor):
    def visit_concrete_component_a(self, element: ConcreteComponentA) -> None:
        result = element.exclusive_method_of_concrete_component_a()
        print(f"ConcreteVisitor2: {result}")

    def visit_concrete_component_b(self, element: ConcreteComponentB) -> None:
        result = element.exclusive_method_of_concrete_component_b()
        print(f"ConcreteVisitor2: {result}")


def client_code(components: list[Component], visitor: Visitor) -> None:
    """Client code can run visitor operations over any set of elements without figuring out their concrete classes."""
    for component in components:
        component.accept(visitor)


if __name__ == "__main__":
    components = [ConcreteComponentA(), ConcreteComponentB()]

    print("The client code works with all visitors via the base Visitor interface:")
    visitor1 = ConcreteVisitor1()
    client_code(components, visitor1)

    print("It allows the same client code to work with different types of visitors:")
    visitor2 = ConcreteVisitor2()
    client_code(components, visitor2)
