from abc import ABC, abstractmethod
from typing import Any


class Strategy(ABC):
    """The Strategy interface declares operations common to all supported versions of some algorithm."""

    @abstractmethod
    def execute(self, data: Any) -> Any: ...


class Context:
    """The Context defines the interface of interest to clients."""

    def __init__(self, strategy: Strategy) -> None:
        """Usually, the Context accepts a strategy through the constructor, but also provides a setter to change it at runtime."""
        self._strategy = strategy

    @property
    def strategy(self):
        """The context maintains a reference to one of the strategy objects. The context does not know the concrete class of a strategy. It should work with all strategies via the Strategy interface."""
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: Strategy) -> None:
        """The Context allows replacing a Strategy object at runtime."""
        self._strategy = strategy

    def execute_strategy(self, data: Any) -> Any:
        """The Context delegates some work to the Strategy object instead of implementing multiple versions of the algorithm on its own."""
        print(f"Context: Executing strategy {self._strategy.__class__.__name__} with data: {data}")
        return self._strategy.execute(data)


class ConcreteStrategyA(Strategy):
    """Concrete Strategies implement the algorithm while following the base Strategy interface. The interface makes them interchangeable in the Context."""

    def execute(self, data: Any) -> Any:
        print(f"ConcreteStrategyA: Processing data {data} in a specific way.")
        return f"Result from ConcreteStrategyA with data {data}"


class ConcreteStrategyB(Strategy):
    """Concrete Strategies implement the algorithm while following the base Strategy interface. The interface makes them interchangeable in the Context."""

    def execute(self, data: Any) -> Any:
        print(f"ConcreteStrategyB: Processing data {data} in a different way.")
        return f"Result from ConcreteStrategyB with data {data}"


if __name__ == "__main__":
    # The client code picks a concrete strategy and passes it to the context. The client should be aware of the differences between strategies in order to make the right choice.
    context = Context(ConcreteStrategyA())
    result_a = context.execute_strategy("Sample Data A")
    print(result_a)

    print("\nSwitching strategy...\n")

    context.strategy = ConcreteStrategyB()
    result_b = context.execute_strategy("Sample Data B")
    print(result_b)
