from abc import ABC, abstractmethod


class Command(ABC):
    """The Command interface declares a method for executing a command."""

    @abstractmethod
    def execute(self) -> None: ...


class Invoker:
    """The Invoker is associated with one or several commands. It sends a request to the command."""

    _on_start: Command | None = None
    _on_finish: Command | None = None

    def set_on_start(self, command: Command) -> None:
        self._on_start = command

    def set_on_finish(self, command: Command) -> None:
        self._on_finish = command

    def do_something_important(self) -> None:
        """The Invoker does not depend on concrete command classes. The Invoker passes a request to a receiver object indirectly, by executing a command."""

        print("Invoker: Does anybody want something done before I begin?")
        if isinstance(self._on_start, Command):
            self._on_start.execute()

        print("Invoker: Doing something really important...")

        print("Invoker: Does anybody want something done after I finish?")
        if isinstance(self._on_finish, Command):
            self._on_finish.execute()


class Receiver:
    """The Receiver classes contain some important business logic. They know how to perform all kinds of operations, associated with carrying out a request. In fact, any class may serve as a Receiver."""

    def do_something(self, a: str) -> None:
        print(f"Receiver: Working on {a}.")

    def do_something_else(self, b: str) -> None:
        print(f"Receiver: Also working on {b}.")


class SimpleCommand(Command):
    """Some commands can implement simple operations on their own."""

    def __init__(self, payload: str) -> None:
        self.payload = payload

    def execute(self) -> None:
        print(f"SimpleCommand: See, I can do simple things like printing ({self.payload})")


class ComplexCommand(Command):
    """However, some commands can delegate more complex operations to other objects, called "receivers"."""

    def __init__(self, receiver: Receiver, a: str, b: str) -> None:
        self.receiver = receiver
        self.a = a
        self.b = b

    def execute(self) -> None:
        print("ComplexCommand: Complex stuff should be done by a receiver object.")
        self.receiver.do_something(self.a)
        self.receiver.do_something_else(self.b)


if __name__ == "__main__":
    # The client code can parameterize an invoker with any commands.
    invoker = Invoker()
    invoker.set_on_start(SimpleCommand("Say Hi!"))
    receiver = Receiver()
    invoker.set_on_finish(ComplexCommand(receiver, "Send email", "Save report"))

    invoker.do_something_important()
