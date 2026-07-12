from abc import ABC, abstractmethod


class Component(ABC):
    """Declares common operations for both simple and complex objects of a composition."""

    @abstractmethod
    def operation(self) -> str:
        """
        Main operation that can be altered by subclasses.
        Optionally can be defined in the base class to provide a default implementation.
        """
        pass

    # Optionally: Component can declare an interface for setting and accessing a parent of the component in a tree structure.
    @property
    def parent(self) -> "Component":
        """Returns the parent of the component in the tree structure."""
        return self._parent

    @parent.setter
    def parent(self, parent: "Component") -> None:
        """Sets the parent of the component in the tree structure."""
        self._parent = parent

    # Optionally: Component can declare an interface for managing child components.
    # This way you don't need to expose any concrete component classes to the client code, even during the tree structure assembly.
    # The downside is that these methods can be empty in the leaf-level components.
    def add(self, component: "Component") -> None:
        """Adds a child component. Default implementation does nothing."""
        pass

    def remove(self, component: "Component") -> None:
        """Removes a child component. Default implementation does nothing."""
        pass

    # Optionally: Component can declare an interface to check if the component can have children.
    def is_composite(self) -> bool:
        """Returns True if the component can have children, False otherwise."""
        return False


class Leaf(Component):
    """Represents leaf objects in the composition. A leaf has no children."""

    def operation(self) -> str:
        """
        Implements the operation defined in the Component interface.

        Usually Leaf objects do the actual work, while Composite objects only delegate to their sub-components.
        """
        return "Leaf"


class Composite(Component):
    """
    Represents complex components that may have children.

    Usually, Composite objects delegate the actual work to their children and then "sum up" the result.
    """

    def __init__(self) -> None:
        """Initializes a new Composite object with an empty list of children."""
        self._children: list[Component] = []

    # A composite object can add or remove other components (both simple and complex) to/from its list of children.
    def add(self, component: Component) -> None:
        """Adds a child component to the composite."""
        self._children.append(component)
        component.parent = self

    def remove(self, component: Component) -> None:
        """Removes a child component from the composite."""
        self._children.remove(component)
        component.parent = None

    def is_composite(self) -> bool:
        """Returns True, indicating that this component can have children."""
        return True

    def operation(self) -> str:
        """Composite travers recursively through all its children and collects their results."""
        results = []
        for child in self._children:
            results.append(child.operation())
        return f"Branch({'+'.join(results)})"


def client_code(component: Component) -> None:
    """Works with all components via the base interface, simple or complex."""
    print(f"RESULT: {component.operation()}", end="")


if __name__ == "__main__":
    # This way the client code can support the simple leaf components...
    simple = Leaf()
    client_code(simple)
    print()

    # ...as well as the complex composites.
    tree = Composite()

    branch1 = Composite()
    branch1.add(Leaf())
    branch1.add(Leaf())

    branch2 = Composite()
    branch2.add(Leaf())

    tree.add(branch1)
    tree.add(branch2)
    client_code(tree)
