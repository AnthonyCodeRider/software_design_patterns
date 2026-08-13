# Examples

## Python standard library - urllib.request

- [OpenerDirector._call_chain](https://github.com/python/cpython/blob/main/Lib/urllib/request.py#L459-L468) / [BaseHandler](https://github.com/python/cpython/blob/main/Lib/urllib/request.py#L575-L591) - `_call_chain` walks an ordered list of handlers registered on the opener, invoking the matching method (`http_open`, `http_error_404`, `unknown_open`, etc.) on each until one returns a non-`None` result; a handler that can't service the request simply returns `None` so the next one in the chain gets a turn. `BaseHandler` subclasses like `HTTPRedirectHandler.redirect_request` and `HTTPDefaultErrorHandler.http_error_default` are the concrete handlers - the docstring for `redirect_request` even states the contract explicitly: "raise HTTPError if no-one else should try to handle this url. Return None if you can't but another Handler might," which is the textbook Chain of Responsibility rule.

## Python standard library - logging

- [Logger.callHandlers](https://github.com/python/cpython/blob/main/Lib/logging/__init__.py#L1740-L1761) - starting at `c = self`, the method walks `c.parent` up the logger hierarchy, offering the `LogRecord` to every handler attached to each logger in turn. Each logger in the chain is a potential handler of the request; a logger stops the propagation only by setting `propagate = False`, otherwise the record keeps travelling up to the root logger exactly like a request travelling down a handler chain until something consumes it (or it falls off the end and CPython emits a "no handlers" warning).

## Django

- [BaseHandler.process_exception_by_middleware](https://github.com/django/django/blob/main/django/core/handlers/base.py#L358-L367) - `self._exception_middleware` is an ordered list of `process_exception` bound methods collected from every installed middleware during `load_middleware`. The method iterates that list calling `middleware_method(request, exception)` and returns as soon as one produces a truthy `response`; if none of them do, it returns `None` and Django falls back to its default 500 handling. Each middleware is a handler that either resolves the exception into a response or defers to the next middleware in the stack, the same shape as `AbstractHandler.handle` delegating to `self._next_handler`.

## Flask

- [Flask._find_error_handler](https://github.com/pallets/flask/blob/main/src/flask/sansio/app.py#L868-L889) - to resolve an error handler for a raised exception, the method searches from most specific to least specific: blueprint-registered handler for the exact HTTP code, then the app-level handler for that code, then blueprint/app handlers for the exception's class walked up its `__mro__`, finally falling back to `None`. Each level of the nested loop is a link in the chain that either supplies a handler (`handler_map.get(cls)` returns non-`None`) or passes responsibility up to the next, broader scope, mirroring how `logging.Logger.callHandlers` climbs a hierarchy until something claims the record.
