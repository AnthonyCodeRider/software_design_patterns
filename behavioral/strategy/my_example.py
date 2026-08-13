from typing import Protocol


# Strategy interface
class RoutePlanner(Protocol):
    def plann_route(self, start: str, end: str) -> None: ...


# Concrete strategy classes
class CarRoutePlanner:
    def plann_route(self, start: str, end: str) -> None:
        print(f"Planning route from {start} to {end} by car.")


class BikeRoutePlanner:
    def plann_route(self, start: str, end: str) -> None:
        print(f"Planning route from {start} to {end} by bike.")


class PublicTransportRoutePlanner:
    def plann_route(self, start: str, end: str) -> None:
        print(f"Planning route from {start} to {end} by public transport.")


# Context class
class RouteContext:
    def __init__(self, strategy: RoutePlanner) -> None:
        self._strategy = strategy

    @property
    def strategy(self) -> RoutePlanner:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: RoutePlanner) -> None:
        self._strategy = strategy

    def plan_route(self, start: str, end: str) -> None:
        print(f"Context: Planning route from {start} to {end} using {self._strategy.__class__.__name__}.")
        self._strategy.plann_route(start, end)


if __name__ == "__main__":
    # Client code
    context = RouteContext(CarRoutePlanner())
    context.plan_route("A", "B")

    print("\nSwitching strategy...\n")

    context.strategy = BikeRoutePlanner()
    context.plan_route("A", "B")

    print("\nSwitching strategy...\n")

    context.strategy = PublicTransportRoutePlanner()
    context.plan_route("A", "B")
