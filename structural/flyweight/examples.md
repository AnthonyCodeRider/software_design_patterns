# Examples

## Python standard library - re

- [\_compile](https://github.com/python/cpython/blob/main/Lib/re/__init__.py#L332-L373) - `_cache`/`_cache2` map `(type(pattern), pattern, flags)` to a compiled `Pattern` object, so repeated calls to `re.search`/`re.sub`/etc. with the same pattern and flags reuse the identical compiled object instead of recompiling. Intrinsic state is the pattern text plus flags; extrinsic state is the subject string passed at match time - a genuine Flyweight, not mere memoization, since the shared object is later invoked with different per-call arguments.

## confluent-kafka-python

- [\_SchemaCache](https://github.com/confluentinc/confluent-kafka-python/blob/master/src/confluent_kafka/schema_registry/common/schema_registry_client.py#L95-L297) - a thread-safe cache with parallel indexes (`schema_id_index`, `schema_guid_index`, `schema_index`, `rs_*_index`) keyed by subject/id/guid/version, all returning the same `Schema`/`RegisteredSchema` object instead of re-deserializing from the registry on every lookup. Intrinsic state is the schema id/guid/subject+version; extrinsic state is whatever the caller does with the returned schema (e.g. serialize a given record).

## Python standard library - enum

- [EnumType.**call**](https://github.com/python/cpython/blob/main/Lib/enum.py#L1178-L1187) - `Color(3)` looks up `cls._value2member_map_[value]` and returns the pre-built canonical member object rather than constructing a new one. All logical "instances" for a given value are the same object - a dict-keyed factory/registry matching Flyweight's structure directly.

## botocore (AWS SDK core, used by boto3)

- [ClientExceptionsFactory](https://github.com/boto/botocore/blob/develop/botocore/errorfactory.py#L57-L76) - `self._client_exceptions_cache` maps `service_name` to a shared object holding all modeled exception classes for that service. Every client created for the same AWS service reuses the identical exceptions container instead of rebuilding the exception class hierarchy each time.
