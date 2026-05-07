from abc import ABC, abstractmethod


class AbstractBuilder(ABC):
    @property
    @abstractmethod
    def product(self):
        pass

    @abstractmethod
    def build_part_a(self):
        pass

    @abstractmethod
    def build_part_b(self):
        pass

    @abstractmethod
    def build_part_c(self):
        pass


class Product1:
    """Use builder design pattern when your products are complex and require extensive configuration."""

    def __init__(self):
        self.parts = []

    def add(self, part: str):
        self.parts.append(part)

    def list_parts(self) -> str:
        return f"Product parts: {', '.join(self.parts)}"


class ConcreteBuilder(AbstractBuilder):
    def __init__(self):
        self._reset()

    def _reset(self):
        self._product = Product1()

    @property
    def product(self) -> Product1:
        """Different builders can create different products that don't follow the same interface."""
        product = self._product
        self._reset()  # This is optional
        return product

    def build_part_a(self):
        self._product.add("PartA1")

    def build_part_b(self):
        self._product.add("PartB1")

    def build_part_c(self):
        self._product.add("PartC1")


class Director:
    """Optional class that defines the order of building steps. It can construct several product variations."""

    def __init__(self, builder: AbstractBuilder):
        self._builder = builder

    def build_minimal_viable_product(self):
        self._builder.build_part_a()

    def build_full_featured_product(self):
        self._builder.build_part_a()
        self._builder.build_part_b()
        self._builder.build_part_c()


if __name__ == "__main__":
    builder = ConcreteBuilder()
    director = Director(builder)

    print("Standard basic product:")
    director.build_minimal_viable_product()
    print(builder.product.list_parts())

    print("\nStandard full featured product:")
    director.build_full_featured_product()
    print(builder.product.list_parts())

    # Remember, the Builder pattern can be used without a Director class.
    print("\nCustom product:")
    builder.build_part_a()
    builder.build_part_c()
    print(builder.product.list_parts())
