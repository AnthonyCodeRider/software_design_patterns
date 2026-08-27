class AbstractClass:
    """
    The AbstractClass defines the template method that contains a skeleton of an algorithm.
    That algorithm consists of a series of steps, some of which are implemented in the abstract class and others are left to be implemented by subclasses.
    """

    def template_method(self):
        """
        The template method defines the skeleton of an algorithm.
        It must not be overridden in subclasses.
        """
        self.base_operation1()
        self.required_operations1()
        self.base_operation2()
        self.hook1()
        self.required_operations2()
        self.base_operation3()
        self.hook2()

    # The base operations already have implementations.
    def base_operation1(self):
        print("AbstractClass: Base operation 1")

    def base_operation2(self):
        print("AbstractClass: Base operation 2")

    def base_operation3(self):
        print("AbstractClass: Base operation 3")

    # These operations have to be implemented in subclasses.
    def required_operations1(self):
        raise NotImplementedError("You should implement this method!")

    def required_operations2(self):
        raise NotImplementedError("You should implement this method!")

    # These are "hooks." Subclasses may override them, but it's not mandatory.
    def hook1(self):
        pass

    def hook2(self):
        pass


class ConcreteClass1(AbstractClass):
    """
    Concrete classes have to implement all abstract operations of the base class.
    They can also override some operations with a default implementation.
    """

    def required_operations1(self):
        print("ConcreteClass1: Implemented operation 1")

    def required_operations2(self):
        print("ConcreteClass1: Implemented operation 2")


class ConcreteClass2(AbstractClass):
    def required_operations1(self):
        print("ConcreteClass2: Implemented operation 1")

    def required_operations2(self):
        print("ConcreteClass2: Implemented operation 2")

    def hook1(self):
        print("ConcreteClass2: Overridden hook 1")


def client_code(concrete_class: AbstractClass) -> None:
    """
    The client code calls the template method to execute the algorithm.
    """
    concrete_class.template_method()


if __name__ == "__main__":
    print("Same client code can work with different subclasses:")
    client_code(ConcreteClass1())
    print("\n")
    print("Same client code can work with different subclasses:")
    client_code(ConcreteClass2())
