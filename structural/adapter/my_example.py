from abc import ABC, abstractmethod


class TypeCPort:
    def connect(self):
        print("Connected to Type C port")


class LightningPort:
    def apple_connect(self):
        print("Connected to Lightning port")


class ConnectionInterface(ABC):
    @abstractmethod
    def connect(self):
        pass


class LightningToTypeCAdapter(ConnectionInterface):
    def __init__(self, lightning_port: LightningPort):
        self.lightning_port = lightning_port

    def connect(self):
        self.lightning_port.apple_connect()


def client_code(wire: ConnectionInterface):
    wire.connect()


if __name__ == "__main__":
    # Using Type C port directly
    type_c_port = TypeCPort()
    client_code(type_c_port)

    # Using Lightning port through adapter
    lightning_port = LightningPort()
    adapter = LightningToTypeCAdapter(lightning_port)
    client_code(adapter)
