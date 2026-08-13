from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Handler(ABC):
    """The interface for building a chain of handlers and executing a request."""

    @abstractmethod
    def set_next(self, handler: "Handler") -> Handler:
        pass

    @abstractmethod
    def handle(self, request: Any) -> str | None:
        pass


class AbstractHandler(Handler):
    """The base handler class implements the default chaining behavior."""

    _next_handler: Handler | None = None

    def set_next(self, handler: Handler) -> Handler:
        self._next_handler = handler
        # Returning a handler from here will let us link handlers in a convenient way like this:
        # monkey.set_next(squirrel).set_next(dog)
        return handler

    def handle(self, request: Any) -> str | None:
        if self._next_handler:
            return self._next_handler.handle(request)

        return None


# Concrete handlers can either handle a request or pass it to the next handler in the chain.


class ConcreteHandler1(AbstractHandler):
    def handle(self, request: Any) -> str | None:
        if request == "concrete request 1":
            return f"ConcreteHandler1: I'll handle the request to {request}."
        return super().handle(request)


class ConcreteHandler2(AbstractHandler):
    def handle(self, request: Any) -> str | None:
        if request == "concrete request 2":
            return f"ConcreteHandler2: I'll handle the request to {request}."
        return super().handle(request)


class ConcreteHandler3(AbstractHandler):
    def handle(self, request: Any) -> str | None:
        if request == "concrete request 3":
            return f"ConcreteHandler3: I'll handle the request to {request}."
        return super().handle(request)


def client_code(handler: Handler) -> None:
    """The client code is usually suited to work with a single handler, it doesn't need to know about the concrete classes of handlers in the chain."""
    for request in ["concrete request 1", "concrete request 2", "unhandled request"]:
        print(f"Client: Who wants to handle the request '{request}'?")
        result = handler.handle(request)
        if result:
            print(f"- {result}")
        else:
            print(f"- {request} was left untouched.")


if __name__ == "__main__":
    concrete_handler1 = ConcreteHandler1()
    concrete_handler2 = ConcreteHandler2()
    concrete_handler3 = ConcreteHandler3()
    concrete_handler1.set_next(concrete_handler2).set_next(concrete_handler3)

    print("Subchain: ConcreteHandler1 > ConcreteHandler2 > ConcreteHandler3")
    client_code(concrete_handler1)
    print("\nSubchain: ConcreteHandler2 > ConcreteHandler3")
    client_code(concrete_handler2)
