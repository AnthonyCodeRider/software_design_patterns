from __future__ import annotations

from abc import ABC, abstractmethod


class CloudAbstraction:
    def __init__(self, cloud_provider: CloudProvider):
        self.cloud_provider = cloud_provider

    def create_bucket(self, bucket_name):
        return self.cloud_provider.create_bucket(bucket_name)

    def delete_bucket(self, bucket_name):
        return self.cloud_provider.delete_bucket(bucket_name)

    def upload_file(self, bucket_name, file_path):
        return self.cloud_provider.upload_file(bucket_name, file_path)


class CloudProvider(ABC):
    @abstractmethod
    def create_bucket(self, bucket_name):
        pass

    @abstractmethod
    def delete_bucket(self, bucket_name):
        pass

    @abstractmethod
    def upload_file(self, bucket_name, file_path):
        pass


class AWSProvider(CloudProvider):
    def create_bucket(self, bucket_name):
        return f"AWS: Created bucket '{bucket_name}'"

    def delete_bucket(self, bucket_name):
        return f"AWS: Deleted bucket '{bucket_name}'"

    def upload_file(self, bucket_name, file_path):
        return f"AWS: Uploaded '{file_path}' to bucket '{bucket_name}'"


class GCPProvider(CloudProvider):
    def create_bucket(self, bucket_name):
        return f"GCP: Created bucket '{bucket_name}'"

    def delete_bucket(self, bucket_name):
        return f"GCP: Deleted bucket '{bucket_name}'"

    def upload_file(self, bucket_name, file_path):
        return f"GCP: Uploaded '{file_path}' to bucket '{bucket_name}'"


class AzureProvider(CloudProvider):
    def create_bucket(self, bucket_name):
        return f"Azure: Created bucket '{bucket_name}'"

    def delete_bucket(self, bucket_name):
        return f"Azure: Deleted bucket '{bucket_name}'"

    def upload_file(self, bucket_name, file_path):
        return f"Azure: Uploaded '{file_path}' to bucket '{bucket_name}'"


def client_code(cloud_abstraction: CloudAbstraction):
    print(cloud_abstraction.create_bucket("my_bucket"))
    print(cloud_abstraction.upload_file("my_bucket", "file.txt"))
    print(cloud_abstraction.delete_bucket("my_bucket"))


if __name__ == "__main__":
    aws_provider = AWSProvider()
    gcp_provider = GCPProvider()
    azure_provider = AzureProvider()

    cloud_abstraction_aws = CloudAbstraction(aws_provider)
    cloud_abstraction_gcp = CloudAbstraction(gcp_provider)
    cloud_abstraction_azure = CloudAbstraction(azure_provider)

    print("Using AWS Provider:")
    client_code(cloud_abstraction_aws)

    print("\nUsing GCP Provider:")
    client_code(cloud_abstraction_gcp)

    print("\nUsing Azure Provider:")
    client_code(cloud_abstraction_azure)
