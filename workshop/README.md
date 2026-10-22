# Design patterns workshop

## Agenda

- Why patterns?
- My personal favorite patterns
- Hands on session
- Results discussion
- Takeaways

## Why patterns? (Short summary)

Design patterns are typical solutions to commonly occurring problems in software.
They are like blueprints that you can customize to solve a recurring problem in your code.

They help you:

- Spot problems in your code.
- Pick a solution that has been tested.
- Communicate your intent to other developers in a common language.
- Avoid reinventing the wheel.

3 categories of patterns:

- Creational: How to create objects in a flexible way.
- Structural: How to compose objects into larger structures.
- Behavioral: How to organize communication between objects.

Recommended resources:

- [Refactoring Guru](https://refactoring.guru/design-patterns) - Classic patterns explained with examples in many languages.
- [ArjanCodes Youtube channel](https://www.youtube.com/@ArjanCodes) - More modern Pythonic examples of patterns.
- [My Github repository with personal notes](https://github.com/AnthonyCodeRider/software_design_patterns) - A collection of generic, personal and real-world examples of patterns in Python.

## My personal favorite patterns

Each pattern below fixes one kind of problem. Spot the problem first, then reach for the pattern.

### Strategy (Behavioral)

**The problem.** An `if/elif` chain that picks between variants of the same job, and grows every time a new variant shows up.

**The fix.** Give every variant the same interface, and let the caller pick one. Adding a variant means adding code, not editing the chain.

```python
PARSERS = {"json": parse_json, "csv": parse_csv}
rows = PARSERS[fmt](raw)
```

In the wild, Airflow's `ExecutorLoader` picks a `BaseExecutor` subclass from config. Notes: [`behavioral/strategy`](../behavioral/strategy/), real examples in [`examples.md`](../behavioral/strategy/examples.md).

### Factory (Creational)

**The problem.** Code that uses an object also decides which class to build and how to configure it. Every new type means editing that code, and the setup details (bucket names, datasets) end up spread across the codebase.

**The fix.** Move creation into one place that takes a name or config and returns an object behind a common interface. Callers ask for "a sink" and never name the concrete class.

```python
SINK_FACTORIES = {"s3": create_s3_sink, "bigquery": create_bigquery_sink}
sink = SINK_FACTORIES[name](topic)
```

In the wild, PySpark's `transformWithState` tests use a `StatefulProcessorFactory` for every processor. Each factory builds a pandas or a row-based variant, and `get(use_pandas)` picks one, so the same test runs against both APIs without naming a concrete class. Notes: [`creational/factory`](../creational/factory/), real examples in [`examples.md`](../creational/factory/examples.md).

### Decorator (Structural)

**The problem.** The same code, such as retries, timing or logging, copy-pasted around several calls.

**The fix.** Wrap the object or function in another one with the same interface that adds the behavior. Wrappers stack.

```python
@timed
@retry(attempts=3)
def write(rows): ...
```

Notes: [`structural/decorator`](../structural/decorator/).

### Template method (Behavioral)

**The problem.** Two classes that run the same steps in the same order, with only a few steps done differently.

**The fix.** Put the fixed sequence in a base class method, and let subclasses override only the steps that differ.

```python
class Sink(ABC):
    def write(self, rows):
        self.open()
        self.send(self.serialize(rows))
        self.close()
```

In the wild, Airflow's `PythonOperator.execute()` fixes the steps for running a task: resolve `op_kwargs` against the context, call the `execute_callable()` hook, and log the result. `PythonVirtualenvOperator` and `ExternalPythonOperator` override only `execute_callable()` to run the function in a fresh virtualenv or an external interpreter, and reuse the rest unchanged. Notes: [`behavioral/template_method`](../behavioral/template_method/), real examples in [`examples.md`](../behavioral/template_method/examples.md).

## Hands-on session

A hands-on session: You get a Kafka message handler that grew without a plan, and you refactor it with design patterns while the tests stay green.

Open [`kata.py`](kata.py). `process_message(topic, raw)` is called once per Kafka message.
It parses the payload, cleans each row, and writes the rows to the sinks configured for the topic.
The sinks talk to `FakeCloud`, an in-memory stand-in for S3 and BigQuery.

Refactor it. Fix as many problems as you can in.
Leave `FakeCloud` as it is.

Rules:

- `uv run --with pytest pytest` stays green.
- Keep the names the tests use: `process_message`, `ValidationError`, `CLOUD` and `FakeCloud`.
- Everything else may change.

Start with the problem that bothers you most. You won't fix everything, and that's fine.

## Results discussion

1. Which problem did you fix first, and why that one?
2. Which pattern did you use? Did anyone fix the same problem with a different pattern?
3. Did any refactor make the code harder to read? Where is the line between structure and indirection?

Reference solutions:

- [`solution_classic.py`](solution_classic.py) uses the GoF shape: an interface and a class for every role.
- [`solution_pythonic.py`](solution_pythonic.py) uses functions, dicts and real `@decorators`. It keeps classes only for Template Method.

Here is the same Strategy in both styles:

```python
# classic
class Parser(Protocol):
    def parse(self, raw: str) -> list[Row]: ...

class JsonParser:
    def parse(self, raw: str) -> list[Row]:
        data = json.loads(raw)
        return data if isinstance(data, list) else [data]

TOPIC_CONFIG = {"orders": TopicConfig(JsonParser(), ...)}
rows = config.parser.parse(raw)
```

```python
# pythonic
Parser = Callable[[str], list[Row]]

def parse_json(raw: str) -> list[Row]:
    data = json.loads(raw)
    return data if isinstance(data, list) else [data]

TOPICS = {"orders": Topic(parse_json, ...)}
rows = config.parse(raw)
```

A function already has one method and no state, so the `Parser` interface collapses into a type alias.

## Takeaways

1. **Python can make patterns lighter.** for example Strategy can be a dict of functions and Factory can be a dict of constructors. There is a syntactic sugar for decorators. Some patterns may still need classes when you need shared state for example.
2. **The patterns are already in our tools.** Airflow executors, Requests auth, PySpark's stateful processor tests and Airflow's `PythonOperator`. Knowing the names makes those codebases easier to read.
3. **Don't force them.** A pattern without the problem it fixes is extra indirection. Reach for one when the problem is clear and the pattern is a good fit.

All 22 patterns from this repo, each with an example and real usages in open-source projects, are in [`creational/`](../creational/), [`structural/`](../structural/) and [`behavioral/`](../behavioral/).

---

## Facilitator notes

**Problems planted in `kata.py`**

| Problem                                                             | Where                        | Pattern         |
| ------------------------------------------------------------------- | ---------------------------- | --------------- |
| `if/elif` on `config["format"]`                                     | `process_message`, `# parse` | Strategy        |
| `if/elif` on sink name, with sinks built and configured inline      | `process_message`, `# write` | Factory         |
| Retry and timing loop copy-pasted per sink                          | `process_message`, `# write` | Decorator       |
| `write_to_s3` and `insert_rows` share open, batch, serialize, close | `S3Sink`, `BigQuerySink`     | Template method |

The Factory fix works best after Template Method. Once both sinks share a `write()` method, the factory can return either one and the caller treats them the same. Point that out if someone starts with Factory.

The `# clean` block is not a planted problem. If someone extracts it into a function, that's fine, but it doesn't need a pattern.

**Things to point out in the results discussion**

- Someone may extract helper functions without using any pattern. That counts. Ask whether adding a fourth format would now mean editing one place or several.
- The pythonic solution puts `@timed` outside `@retry`, so it measures all attempts together. The kata timed each attempt. Swapping the decorator order changes the behavior, which makes a good question for the group.
- In the classic solution, the decorators wrap the sink at call time (`TimedWriter(RetryingWriter(factory.create(topic)))`). In the pythonic one, they're fixed on `Sink.write`. Ask which is easier to change per topic.
- Strategy and Factory both replace an `if/elif` with a lookup, so people may mix them up. Strategy is about swapping behavior behind one interface. Factory is about who builds the object and with which settings. In the pythonic solution, `SINK_FACTORIES` uses `functools.partial` to bake in the bucket and dataset, and that configuration is what makes it a factory rather than a plain lookup.
