from abc import ABC, abstractmethod


class AbstractService(ABC):
    """Abstract service interface."""

    @abstractmethod
    def operation(self) -> str:
        """Perform an operation."""
        pass


class RealService(AbstractService):
    """Real service implementation."""

    def operation(self) -> str:
        """Perform the actual heavy operation."""
        return "RealService: Performing operation."


class ProxyService(AbstractService):
    """Proxy service that controls access to the RealService."""

    def __init__(self, real_service: RealService):
        self._real_service = real_service

    def operation(self) -> str:
        """Control access to the RealService and perform additional actions, access checks, lazy loading, logging, etc."""
        # Here you can add any additional logic before or after calling the real service
        print("ProxyService: Checking access before calling RealService.")
        if self._check_access():
            result = self._real_service.operation()
        print("ProxyService: Logging after calling RealService.")
        return result

    def _check_access(self) -> bool:
        """Check if the client has access to the RealService."""
        # Implement access control logic here
        return True


def client_code(service: AbstractService) -> None:
    service.operation()


if __name__ == "__main__":
    real_service = RealService()
    proxy_service = ProxyService(real_service)
    # Client code can work with both RealService and ProxyService without knowing the difference
    client_code(real_service)
    client_code(proxy_service)
