class Target:
    """Used by client"""

    def request(self):
        return "Target: The default target's behavior."


class Adaptee:
    """Contains useful behavior, but its interface is incompatible with the existing client code."""

    def specific_request(self):
        return ".eetpadA eht fo roivaheb laicepS"


class Adapter(Target, Adaptee):
    """Adapt the interface of Adaptee to the Target's interface."""

    def request(self):
        return f"Adapter: (TRANSLATED) {self.specific_request()[::-1]}"


def client_code(target: Target) -> None:
    print(target.request())


if __name__ == "__main__":
    # Client code can work with target
    client_code(Target())

    # Client cannot work with Adaptee
    try:
        client_code(Adaptee())
    except AttributeError as e:
        print(f"Client: {e}")

    # But client can work with Adapter
    client_code(Adapter())
