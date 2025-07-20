class Freight:
    def __init__(self, distance: float, weight: float):
        if distance <= 0 or weight <= 0:
            raise ValueError("Distance and weight must be positive values.")
        self._distance: float = distance
        self._weight: float = weight
        self._type: str = ""
        self._value: float = 0.0

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, value: str) -> None:
        self._type = value

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        self._value = value

    @property
    def distance(self) -> float:
        return self._distance

    @distance.setter
    def distance(self, value: float) -> None:
        self._distance = value

    @property
    def weight(self) -> float:
        return self._weight

    @weight.setter
    def weight(self, value: float) -> None:
        self._weight = value

    def calculate_price(self) -> float:
        if "Normal" == self._type:
            self._value = self._distance * self._weight + 5
        elif "Sedex" == self._type:
            self._value = self._distance * self._weight + 10
        elif "Sedex10" == self._type:
            self._value = self._distance * self._weight + 15
        return self._value
