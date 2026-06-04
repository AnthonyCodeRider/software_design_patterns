class Component:
    """Base component class that defines an interface."""

    def operation(self): ...


class ConcreteComponent(Component):
    """Concrete component provides a default implementation of the interface."""

    def operation(self):
        print("Executing plain component")


class BaseDecorator:
    """
    Base decorator class follows the same interface as other components.
    The purpose is to define the wrapping interface.
    """

    _component: Component = None

    def __init__(self, component: Component):
        self._component = component

    @property
    def component(self) -> Component:
        return self._component

    def operation(self):
        return self.component.operation()


class ConcreteDecorator1(BaseDecorator):
    """Concrete decorators call the wrapped object and alter its result in some way."""

    def operation(self):
        """
        Decorators may call the parent's implementation instead of calling the wrapped object directly.
        It simplifies extension of decorator classes.
        """
        print("Decorator can add new logic BEFORE the call to a wrapped object")
        self.component.operation()


class ConcreteDecorator2(BaseDecorator):
    def operation(self):
        self.component.operation()
        print("Decorator can add new logic AFTER the call to a wrapped object")


def client(component: Component):
    """Client works with the component interface to stay independent of the concrete components"""
    # ...
    component.operation()
    # ...


if __name__ == "__main__":
    simple_component = ConcreteComponent()
    print("Client: I've got a simple component...")
    simple_component.operation()
    print()

    decorator1 = ConcreteDecorator1(simple_component)
    decorator2 = ConcreteDecorator2(decorator1)
    print("Client: I've got a decorated component...")
    client(decorator2)
    print()

    # or like this
    decorated_component = ConcreteDecorator1(ConcreteDecorator2(ConcreteComponent()))
    print("Client: I've got another decorated component...")
    client(decorated_component)
