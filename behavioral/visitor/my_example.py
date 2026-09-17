from __future__ import annotations

from typing import Protocol


class Component(Protocol):
    def accept(self, visitor: Visitor) -> None: ...


class Visitor(Protocol):
    def visit_postgresql(self, postgresql: PostgreSQL) -> None: ...

    def visit_mysql(self, mysql: MySQL) -> None: ...

    def visit_bigquery(self, bq: BigQuery) -> None: ...


class ExportCSV:
    def visit_postgresql(self, postgresql: PostgreSQL) -> None:
        postgresql.query_data()
        print("Exporting PostgreSQL data to CSV format.")

    def visit_mysql(self, mysql: MySQL) -> None:
        mysql.query_data()
        print("Exporting MySQL data to CSV format.")

    def visit_bigquery(self, bq: BigQuery) -> None:
        bq.query_data()
        print("Exporting BigQuery data to CSV format.")


class ExportJSON:
    def visit_postgresql(self, postgresql: PostgreSQL) -> None:
        postgresql.query_data()
        print("Exporting PostgreSQL data to JSON format.")

    def visit_mysql(self, mysql: MySQL) -> None:
        mysql.query_data()
        print("Exporting MySQL data to JSON format.")

    def visit_bigquery(self, bq: BigQuery) -> None:
        bq.query_data()
        print("Exporting BigQuery data to JSON format.")


class PostgreSQL:
    def accept(self, visitor: Visitor) -> None:
        """Double dispatch"""
        visitor.visit_postgresql(self)

    def query_data(self) -> None:
        print("Querying data from PostgreSQL database.")


class MySQL:
    def accept(self, visitor: Visitor) -> None:
        """Double dispatch"""
        visitor.visit_mysql(self)

    def query_data(self) -> None:
        print("Querying data from MySQL database.")


class BigQuery:
    def accept(self, visitor: Visitor) -> None:
        """Double dispatch"""
        visitor.visit_bigquery(self)

    def query_data(self) -> None:
        print("Querying data from BigQuery database.")


def main():
    postgresql = PostgreSQL()
    mysql = MySQL()
    bq = BigQuery()

    databases = [postgresql, mysql, bq]

    print("Exporting data to CSV format:")
    csv_exporter = ExportCSV()
    for db in databases:
        db.accept(csv_exporter)

    print("Exporting data to JSON format:")
    json_exporter = ExportJSON()
    for db in databases:
        db.accept(json_exporter)


if __name__ == "__main__":
    main()
