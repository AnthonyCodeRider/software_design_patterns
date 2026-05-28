# Examples

## Apache Airflow

- [PostgresHook](https://github.com/apache/airflow/blob/main/providers/postgres/src/airflow/providers/postgres/hooks/postgres.py#L98) - A facade for interacting with a PostgreSQL database, providing a simplified interface for executing queries and managing connections. Wraps raw DBAPI connections, credentials retrieval from Airflow's Connection registry, cursor management, SSL config, and IAM auth. You call hook.get_conn() instead of assembling all of that yourself

- [S3Hook](https://github.com/apache/airflow/blob/main/providers/amazon/src/airflow/providers/amazon/aws/hooks/s3.py#L164)

- Every provider (MySQL, Snowflake, etc.) follows the same facade contract via BaseHook.
