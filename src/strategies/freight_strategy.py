from abc import ABC, abstractmethod


class FreightStrategy(ABC):
    @abstractmethod
    def calculate(self, distance: float, weight: float) -> float:
        pass
