from typing import Dict, Type

from exceptions import FreightTypeInvalidError
from strategies.freight_calulator import (
    NormalFreight,
    SedexFreight,
    Sedex10Freight,
)
from strategies.freight_strategy import FreightStrategy


class FreightStrategyFactory:
    def __init__(self):
        self._strategies: Dict[int, Type[FreightStrategy]] = {
            1: NormalFreight,
            2: SedexFreight,
            3: Sedex10Freight,
        }

    def create_strategy(self, option: int) -> FreightStrategy:
        if option not in self._strategies:
            raise FreightTypeInvalidError("Invalid freight option.")

        return self._strategies[option]()
