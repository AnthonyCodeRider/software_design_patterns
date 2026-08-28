from abc import ABC, abstractmethod


class Context:
    """
    The Context defines the interface of interest to clients.
    It maintains a reference to an instance of a State subclass, which represents the current state of the Context.
    """

    _state = None

    def __init__(self, state: "State") -> None:
        self.transition_to(state)

    def transition_to(self, state: "State") -> None:
        """
        The Context allows changing the State object at runtime.
        """
        print(f"Context: Transition to {type(state).__name__}.")
        self._state = state
        self._state.context = self

    def request1(self) -> None:
        """
        The Context delegates part of its behavior to the current State object.
        """
        self._state.handle1()

    def request2(self) -> None:
        self._state.handle2()


class State(ABC):
    """
    The base State class declares methods that all Concrete State should implement.
    It also provides a backreference to the Context object, associated with the State.
    This backreference can be used by States to transition the Context to another State.
    """

    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context

    @abstractmethod
    def handle1(self) -> None:
        pass

    @abstractmethod
    def handle2(self) -> None:
        pass


class ConcreteStateA(State):
    """
    Concrete States implement various behaviors, associated with a state of the Context.
    """

    def handle1(self) -> None:
        print("ConcreteStateA handles request1.")
        print("ConcreteStateA wants to change the state of the context.")
        self.context.transition_to(ConcreteStateB())

    def handle2(self) -> None:
        print("ConcreteStateA handles request2.")


class ConcreteStateB(State):
    def handle1(self) -> None:
        print("ConcreteStateB handles request1.")

    def handle2(self) -> None:
        print("ConcreteStateB handles request2.")
        print("ConcreteStateB wants to change the state of the context")
        self.context.transition_to(ConcreteStateA())


if __name__ == "__main__":
    # The client code.

    context = Context(ConcreteStateA())
    context.request1()
    context.request2()
