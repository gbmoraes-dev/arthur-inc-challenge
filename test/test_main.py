import pytest
from unittest.mock import patch

from main import generate_freight
from exceptions import ExternalAPIError


class TestFreight:
    @pytest.mark.parametrize(
        "weight, distance, option, type, expected_value",
        [
            (2.0, 500, 1, "Normal", 1005.00),
            (2.0, 500, 2, "Sedex", 1010.00),
            (3.4, 500, 3, "Sedex10", 1715.00),
        ],
        ids=["Normal", "Sedex", "Sedex10"],
    )
    def test_generate_freight_with_valid_options(
        self, weight, distance, option, type, expected_value
    ):
        result = generate_freight(weight=weight, distance=distance, option=option)
        assert result == f"The freight value is {expected_value:.2f}"

    def test_invalid_weight_input(self):
        weight = -3
        distance = 500
        option = 3
        with pytest.raises(ValueError):
            generate_freight(weight=weight, distance=distance, option=option)

    def test_invalid_option_input(self):
        weight = 4
        distance = 500
        option = 0
        with pytest.raises(ValueError):
            generate_freight(weight=weight, distance=distance, option=option)

    def test_invalid_distance_input(self):
        weight = 4.2
        distance = 0
        option = 3
        with pytest.raises(ValueError):
            generate_freight(weight=weight, distance=distance, option=option)

    def test_non_numeric_input(self):
        weight = "abc"
        distance = 500
        option = 1
        with pytest.raises(TypeError):
            generate_freight(weight=weight, distance=distance, option=option)

    def test_null_input(self):
        weight = None
        distance = 500
        option = 1
        with pytest.raises(TypeError):
            generate_freight(weight=weight, distance=distance, option=option)

    @patch("main.get_distance_between_ceps")
    def test_generate_freight_with_cep(self, mock_get_distance):
        mock_get_distance.return_value = 430.0

        origin_cep = "01001000"
        destination_cep = "20040030"
        weight = 5.0
        option = 2

        expected_value = 2160.0

        result = generate_freight(
            weight=weight,
            option=option,
            origin_cep=origin_cep,
            destination_cep=destination_cep,
        )
        assert result == f"The freight value is {expected_value:.2f}"

    @patch("main.get_distance_between_ceps", side_effect=ExternalAPIError("Test error"))
    def test_generate_freight_with_api_error(self, mock_get_distance):
        with pytest.raises(ExternalAPIError):
            generate_freight(
                weight=5.0, option=1, origin_cep="01001000", destination_cep="20040030"
            )
