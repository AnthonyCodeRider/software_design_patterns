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


class DataEngineerHandler(AbstractHandler):
    def handle(self, request: Any) -> str | None:
        if request == "process data":
            return f"DataEngineer: I'll handle the request to {request}."
        return super().handle(request)


class DataAnalystHandler(AbstractHandler):
    def handle(self, request: Any) -> str | None:
        if request == "analyze data":
            return f"DataAnalyst: I'll handle the request to {request}."
        return super().handle(request)


class DataScientistHandler(AbstractHandler):
    def handle(self, request: Any) -> str | None:
        if request == "build model":
            return f"DataScientist: I'll handle the request to {request}."
        return super().handle(request)


class WebDeveloperHandler(AbstractHandler):
    def handle(self, request: Any) -> str | None:
        if request == "build API":
            return f"WebDeveloper: I'll handle the request to {request}."
        return super().handle(request)


def client_code(handler: Handler) -> None:
    """The client code is usually suited to work with a single handler, it doesn't need to know about the concrete classes of handlers in the chain."""
    for request in ["process data", "analyze data", "build model", "build API", "unknown request"]:
        print(f"Client: Who wants to handle the request '{request}'?")
        result = handler.handle(request)
        if result:
            print(f"- {result}")
        else:
            print(f"- {request} was left untouched.")


if __name__ == "__main__":
    data_engineer = DataEngineerHandler()
    data_analyst = DataAnalystHandler()
    data_scientist = DataScientistHandler()
    web_developer = WebDeveloperHandler()
    data_engineer.set_next(data_analyst).set_next(data_scientist).set_next(web_developer)

    print("Chain: DataEngineer > DataAnalyst > DataScientist > WebDeveloper")
    client_code(data_engineer)
    print("\nSubchain: DataAnalyst > DataScientist > WebDeveloper")
    client_code(data_scientist)
