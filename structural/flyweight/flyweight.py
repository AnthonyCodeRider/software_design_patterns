"""Use this pattern only if you need to minimize memory usage."""


class Flyweight:
    """The Flyweight class represents the shared state (intrinsic state) of the multiple objects."""

    def __init__(self, shared_state):
        self._shared_state = shared_state

    def operation(self, unique_state):
        """The Flyweight accepts the unique state (extrinsic state) as an argument and uses it in its operation."""
        print(f"Flyweight: Displaying shared ({self._shared_state}) and unique ({unique_state}) state.")


class FlyweightFactory:
    """The FlyweightFactory creates and manages the Flyweight objects."""

    _flyweights: dict[str, Flyweight] = {}

    def __init__(self, initial_flyweights: list[list[str]]):
        for state in initial_flyweights:
            self._flyweights[self.get_key(state)] = Flyweight(state)

    def get_key(self, state):
        """Returns a Flyweight's key for a given shared state."""
        return "-".join(sorted(state))  # can be hashed for better performance

    def get_flyweight(self, shared_state):
        """Returns a Flyweight object with the given shared state or creates a new one if it doesn't exist."""
        key = self.get_key(shared_state)

        if not self._flyweights.get(key):
            print("FlyweightFactory: Can't find a flyweight, creating new one.")
            self._flyweights[key] = Flyweight(shared_state)
        else:
            print("FlyweightFactory: Reusing the existing flyweight.")

        return self._flyweights[key]

    def list_flyweights(self):
        """Lists all the flyweights currently in the factory."""
        count = len(self._flyweights)
        print(f"FlyweightFactory: I have {count} flyweights:")

        for key in self._flyweights:
            print(key)


def client_code(factory: FlyweightFactory, shared_state, unique_state):
    """Client code uses the FlyweightFactory to get a Flyweight object and then calls its operation method."""
    flyweight = factory.get_flyweight(shared_state)
    flyweight.operation(unique_state)


if __name__ == "__main__":
    """The client code usually creates a bunch of pre-populated flyweights in the initialization stage of the application."""
    initial_flyweights = [
        ["Brand1", "Model1", "Color1"],
        ["Brand2", "Model2", "Color2"],
        ["Brand3", "Model3", "Color3"],
    ]
    factory = FlyweightFactory(initial_flyweights)
    factory.list_flyweights()

    client_code(factory, ["Brand1", "Model1", "Color1"], "UniqueState1")
    client_code(factory, ["Brand2", "Model2", "Color2"], "UniqueState2")
    client_code(factory, ["Brand4", "Model4", "Color4"], "UniqueState4")

    factory.list_flyweights()
