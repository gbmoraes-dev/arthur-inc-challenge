from strategies.freight_calulator import (
    NormalFreight,
    Sedex10Freight,
    SedexFreight,
)


class TestFreightStrategy:
    def test_normal_freight_calculation(self):
        strategy = NormalFreight()
        distance = 500.0
        weight = 2.0

        expected_value = 1005.00  # 500 * 2 + 5

        assert strategy.calculate(distance, weight) == expected_value

    def test_sedex_freight_calculation(self):
        strategy = SedexFreight()
        distance = 500.0
        weight = 2.0

        expected_value = 1010.00  # 500 * 2 + 10

        assert strategy.calculate(distance, weight) == expected_value

    def test_sedex10_freight_calculation(self):
        strategy = Sedex10Freight()
        distance = 500.0
        weight = 3.4

        expected_value = 1715.00  # 500 * 3.4 + 15

        assert strategy.calculate(distance, weight) == expected_value
