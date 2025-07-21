import pytest
from unittest.mock import patch, MagicMock

from exceptions import FreightTypeInvalidError
from main import generate_freight


class TestIntegrationFrete:
    @patch("main.BrasilApiProvider")
    def test_generate_freight_end_to_end(self, mock_provider_class):
        mock_provider = MagicMock()
        mock_provider_class.return_value = mock_provider

        with patch(
            "main.get_distance_between_ceps", return_value=100.0
        ) as mock_distance:
            result = generate_freight(
                weight=5.0, option=1, origin_cep="01001000", destination_cep="20021000"
            )

            assert "505.00" in result

            mock_distance.assert_called_once()

            mock_distance.reset_mock()

            with pytest.raises(FreightTypeInvalidError):
                generate_freight(
                    weight=5.0,
                    option=4,
                    origin_cep="01001000",
                    destination_cep="20021000",
                )
