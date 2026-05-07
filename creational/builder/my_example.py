from abc import ABC, abstractmethod


class CarBuilder(ABC):
    @property
    @abstractmethod
    def car(self):
        pass

    @abstractmethod
    def build_engine(self):
        pass

    @abstractmethod
    def build_wheels(self):
        pass

    @abstractmethod
    def build_body(self):
        pass


class SportCar: ...


class SportCarBuilder(CarBuilder):
    def __init__(self):
        self._reset()

    def _reset(self):
        self._car = SportCar()

    @property
    def car(self) -> SportCar:
        car = self._car
        self._reset()
        return car

    def build_engine(self):
        print("Building sport car engine")

    def build_wheels(self):
        print("Building sport car wheels")

    def build_body(self):
        print("Building sport car body")


class SUVCar: ...


class SUVCarBuilder(CarBuilder):
    def __init__(self):
        self._reset()

    def _reset(self):
        self._car = SUVCar()

    @property
    def car(self) -> SUVCar:
        car = self._car
        self._reset()
        return car

    def build_engine(self):
        print("Building SUV car engine")

    def build_wheels(self):
        print("Building SUV car wheels")

    def build_body(self):
        print("Building SUV car body")


class CarDirector:
    def __init__(self, builder: CarBuilder):
        self._builder = builder

    def build_engine(self):
        self._builder.build_engine()

    def build_car(self):
        self._builder.build_engine()
        self._builder.build_wheels()
        self._builder.build_body()

    def change_builder(self, builder: CarBuilder):
        self._builder = builder


if __name__ == "__main__":
    sport_car_builder = SportCarBuilder()
    suv_car_builder = SUVCarBuilder()

    director = CarDirector(sport_car_builder)
    director.build_car()
    sport_car_1 = sport_car_builder.car
    director.build_car()
    sport_car_2 = sport_car_builder.car

    director.change_builder(suv_car_builder)
    director.build_engine()
    suv_car = suv_car_builder.car
