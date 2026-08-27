from abc import ABC, abstractmethod


class AbstractIngestion(ABC):
    def ingest(self):
        self.connect()
        try:
            watermark = self.get_last_watermark()
            rows = self.read_data_since(watermark)
            rows = self.deduplicate(rows)
            self.write_data(rows)
            self.save_watermark(rows)
        finally:
            self.close_connection()

    # The base operations already have implementations.
    def get_last_watermark(self):
        print("Getting the last watermark...")
        return "2024-01-01T00:00:00Z"

    def save_watermark(self, rows: list):
        print("Saving the new watermark...")
        watermark = rows[-1] if rows else None
        print(f"New watermark saved: {watermark}")

    # These operations have to be implemented in subclasses.
    @abstractmethod
    def connect(self): ...

    @abstractmethod
    def close_connection(self): ...

    @abstractmethod
    def read_data_since(self, watermark: str): ...

    @abstractmethod
    def write_data(self, rows: list): ...

    # Optional hook method for deduplication
    def deduplicate(self, rows: list):
        return rows  # Default implementation does nothing


class PostgresCdcSourceIngestion(AbstractIngestion):
    def connect(self):
        print("Connecting to Postgres CDC source...")

    def close_connection(self):
        print("Closing connection to Postgres CDC source...")

    def read_data_since(self, watermark: str):
        print(f"Reading data from Postgres CDC source since {watermark}...")
        return ["row1", "row2", "row3"]

    def write_data(self, rows: list):
        print(f"Writing data to BQ: {rows}")

    def deduplicate(self, rows: list):
        print("Deduplicating rows...")
        return list(dict.fromkeys(rows))  # Simple deduplication using dict to preserve order


class S3SourceIngestion(AbstractIngestion):
    def connect(self):
        print("Connecting to S3 source...")

    def close_connection(self):
        print("Closing connection to S3 source...")

    def read_data_since(self, watermark: str):
        print(f"Reading data from S3 source since {watermark}...")
        return ["rowA", "rowB", "rowC"]

    def write_data(self, rows: list):
        print(f"Writing data to GCS: {rows}")


class APISourceIngestion(AbstractIngestion):
    def connect(self):
        print("Connecting to API source...")

    def close_connection(self):
        print("Closing connection to API source...")

    def read_data_since(self, watermark: str):
        print(f"Reading data from API source since {watermark}...")
        result = []
        for response in self.paginate_api(watermark):
            result.extend(response)
        return result

    def paginate_api(self, watermark: str):
        print(f"Paginating API responses since {watermark}...")
        yield ["rowX", "rowY"]
        yield ["rowZ"]

    def write_data(self, rows: list):
        print(f"Writing data to BQ: {rows}")


def client_code(ingestion: AbstractIngestion) -> None:
    ingestion.ingest()


if __name__ == "__main__":
    print("Ingesting from Postgres CDC source:")
    postgres_ingestion = PostgresCdcSourceIngestion()
    client_code(postgres_ingestion)

    print("\nIngesting from S3 source:")
    s3_ingestion = S3SourceIngestion()
    client_code(s3_ingestion)

    print("\nIngesting from API source:")
    api_ingestion = APISourceIngestion()
    client_code(api_ingestion)
