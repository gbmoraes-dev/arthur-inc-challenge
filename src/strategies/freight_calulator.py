from strategies.freight_strategy import FreightStrategy


class NormalFreight(FreightStrategy):
    def calculate(self, distance: float, weight: float) -> float:
        return distance * weight + 5


class SedexFreight(FreightStrategy):
    def calculate(self, distance: float, weight: float) -> float:
        return distance * weight + 10


class Sedex10Freight(FreightStrategy):
    def calculate(self, distance: float, weight: float) -> float:
        return distance * weight + 15
