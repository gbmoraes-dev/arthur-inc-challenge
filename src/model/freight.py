from typing import cast

from exceptions import DistanceInvalidError, WeightInvalidError
from strategies.freight_strategy import FreightStrategy


class Freight:
    def __init__(self, distance: float, weight: float, strategy: FreightStrategy):
        if distance <= 0:
            raise DistanceInvalidError("Distance must be a positive value.")
        if weight <= 0:
            raise WeightInvalidError("Weight must be a positive value.")
        self._distance = distance
        self._weight = weight
        self._value = cast(float, strategy.calculate(distance, weight))

    @property
    def value(self) -> float:
        return self._value

    @property
    def distance(self) -> float:
        return self._distance

    @property
    def weight(self) -> float:
        return self._weight
