from __future__ import annotations


class Facade:
    """Facade provides a simplified (but limited) interface to complex subsystems"""

    def __init__(self, sub_system1: SubSystem1 = None, sub_system2: SubSystem2 = None):
        """Facade can be provided with the existing sub system objects from client or it can be forced to create them"""
        self.sub_system1 = sub_system1 or SubSystem1()
        self.sub_system2 = sub_system2 or SubSystem2()

    def operation(self):
        """Convenient shortcut to the sub systems's complex logic"""
        self.sub_system1.operation1()
        self.sub_system2.operation1()
        self.sub_system1.operation2()
        self.sub_system2.operation2()


class SubSystem1:
    """SubSystem's technically can be used by either client or facade. Facade is just another client. Often subsystems can be third-party frameworks or libraries"""

    def operation1(self):
        print(f"{self.__class__.__name__} performs {self.operation1.__name__}")

    def operation2(self):
        print(f"{self.__class__.__name__} performs {self.operation2.__name__}")

    # other operations that are not used by Facade
    # ...


class SubSystem2:
    """Facade can work with multiple subsytems and their whole eco system"""

    def operation1(self):
        print(f"{self.__class__.__name__} performs {self.operation1.__name__}")

    def operation2(self):
        print(f"{self.__class__.__name__} performs {self.operation2.__name__}")

    # other operations that are not used by Facade
    # ...


def client(facade: Facade):
    facade.operation()


if __name__ == "__main__":
    sub_system1 = SubSystem1()  # Can be already instantiated
    facade = Facade(sub_system1=sub_system1)
    client(facade)
