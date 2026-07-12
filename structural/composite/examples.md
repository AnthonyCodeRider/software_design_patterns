# Examples

## Apache Airflow

- [TaskGroup](https://github.com/apache/airflow/blob/main/task-sdk/src/airflow/sdk/definitions/taskgroup.py) / [BaseOperator](https://github.com/apache/airflow/blob/main/task-sdk/src/airflow/sdk/definitions/baseoperator.py) - `TaskGroup` subclasses the same `DAGNode` base that `BaseOperator` implements, and holds `children: dict[str, DAGNode]` whose values can be individual operators or further nested `TaskGroup`s. Both fulfil the shared `DependencyMixin` contract (`roots`, `leaves`, upstream/downstream wiring), so a whole group of tasks can be wired into a DAG exactly like a single task.

## Python standard library - unittest

- [TestSuite](https://github.com/python/cpython/blob/main/Lib/unittest/suite.py) / [TestCase](https://github.com/python/cpython/blob/main/Lib/unittest/case.py) - `TestSuite` and `TestCase` both implement `run()` and `countTestCases()`. `TestSuite` holds a list of children (`self._tests`) that can be `TestCase` leaves or further nested `TestSuite`s, and recurses over them uniformly in both methods - one of the cleanest Composite examples in the stdlib.

## Click

- [Group](https://github.com/pallets/click/blob/main/src/click/core.py) / [Command](https://github.com/pallets/click/blob/main/src/click/core.py) - `Group` subclasses `Command` directly and holds `self.commands: dict[str, Command]`, whose values can be plain commands or further nested `Group`s. Every node answers to the same `invoke()`/`get_help()`, so a CLI subcommand tree of arbitrary depth is dispatched uniformly.

## Starlette / FastAPI

- [Route](https://github.com/encode/starlette/blob/master/starlette/routing.py) / [Mount](https://github.com/encode/starlette/blob/master/starlette/routing.py) - Both subclass `BaseRoute` and implement `matches()`/`handle()`. `Mount` wraps a child `Router` whose `routes` list can hold more `Route`s or nested `Mount`s (e.g. via FastAPI's `include_router`), so request dispatch treats a single endpoint and an entire mounted sub-application identically.
