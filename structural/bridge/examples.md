# Examples

## matplotlib

- [Figure](https://github.com/matplotlib/matplotlib/blob/main/lib/matplotlib/figure.py) / [FigureCanvasBase](https://github.com/matplotlib/matplotlib/blob/main/lib/matplotlib/backend_bases.py) / [FigureCanvasAgg](https://github.com/matplotlib/matplotlib/blob/main/lib/matplotlib/backends/backend_agg.py) - `Figure` (and the `Artist` hierarchy it draws) is the abstraction; it holds a reference to a canvas object (`self.canvas`) that implements the actual rendering. `FigureCanvasBase` defines the implementor interface, and separate backend hierarchies (`FigureCanvasAgg`, plus Qt/PDF/SVG/Cairo variants) implement it independently - you can swap backends without touching `Figure`/`Artist` code, and add new figure-level artists without touching backends.

## SQLAlchemy

- [Engine](https://github.com/sqlalchemy/sqlalchemy/blob/main/lib/sqlalchemy/engine/base.py) / [Dialect](https://github.com/sqlalchemy/sqlalchemy/blob/main/lib/sqlalchemy/engine/interfaces.py) - `Engine` (and `Connection`) is the abstraction that application code talks to; it holds a `self.dialect: Dialect` reference and delegates all database/DBAPI-specific behavior to it. `Dialect` is a separate implementor hierarchy (`PGDialect`, `MySQLDialect`, `SQLiteDialect`, etc.) that can be extended with new database backends without changing `Engine`/`Connection`.

## Django

- [BaseDatabaseWrapper](https://github.com/django/django/blob/main/django/db/backends/base/base.py) / [BaseDatabaseOperations](https://github.com/django/django/blob/main/django/db/backends/base/operations.py) - `BaseDatabaseWrapper` composes several swappable implementor objects (`self.ops`, `.features`, `.client`, `.creation`, `.introspection`) rather than relying only on subclassing the wrapper itself. Each vendor backend (postgresql, mysql, sqlite3) supplies its own `DatabaseOperations`/`DatabaseFeatures` implementor subclasses, so the operations hierarchy and the wrapper hierarchy vary independently.

## Python standard library - logging

- [Handler](https://github.com/python/cpython/blob/main/Lib/logging/__init__.py) / [Formatter](https://github.com/python/cpython/blob/main/Lib/logging/__init__.py) - `Handler` is the abstraction hierarchy (`StreamHandler`, `FileHandler`, `SocketHandler`, `SMTPHandler`, ...) responsible for "where records go"; it holds `self.formatter` (set via `setFormatter`) and delegates the "how to render a record to text" work to it in `Handler.format()`. `Formatter` is a fully independent implementor hierarchy - any handler can be paired with any formatter, and both sides are extended separately, which is what makes this genuinely Bridge rather than Strategy.
