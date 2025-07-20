import pytest
from unittest.mock import patch

from exceptions import ExternalAPIError, FreightTypeInvalidError
from main import generate_freight
from provider.services.brasil_api import BrasilApiProvider


class TestIntegrationFrete:
    @pytest.mark.integration
    def test_generate_freight(self):
        origin_cep = "22041001"  # Av. Atlântica, Copacabana, Rio de Janeiro
        destination_cep = "01310200"  # Av. Paulista, São Paulo
        weight = 5.0
        option = 2

        result_str = generate_freight(
            weight=weight,
            option=option,
            origin_cep=origin_cep,
            destination_cep=destination_cep,
        )

        assert "The freight value is" in result_str

        value_str = result_str.split("is ")[-1]
        value = float(value_str)

        assert isinstance(value, float)
        assert value > 0

    @pytest.mark.integration
    def test_generate_freight_with_different_options(self):
        origin_cep = "22041001"  # Av. Atlântica, Copacabana, Rio de Janeiro
        destination_cep = "01310200"  # Av. Paulista, São Paulo
        weight = 3.0

        for option in [1, 2, 3]:
            result_str = generate_freight(
                weight=weight,
                option=option,
                origin_cep=origin_cep,
                destination_cep=destination_cep,
            )

            assert "The freight value is" in result_str

            value_str = result_str.split("is ")[-1]
            value = float(value_str)

            assert isinstance(value, float)
            assert value > 0

            if option == 1:
                normal_value = value
            elif option == 2:
                sedex_value = value
                assert sedex_value > normal_value
            else:
                sedex10_value = value
                assert sedex10_value > sedex_value

    @pytest.mark.integration
    def test_generate_freight_with_different_weights(self):
        """Testa o cálculo de frete com diferentes pesos usando APIs reais."""
        origin_cep = "22041001"  # Av. Atlântica, Copacabana, Rio de Janeiro
        destination_cep = "01310200"  # Av. Paulista, São Paulo
        option = 2

        weights = [1.0, 5.0, 10.0]
        previous_value = 0

        for weight in weights:
            result_str = generate_freight(
                weight=weight,
                option=option,
                origin_cep=origin_cep,
                destination_cep=destination_cep,
            )

            assert "The freight value is" in result_str

            value_str = result_str.split("is ")[-1]
            value = float(value_str)

            assert isinstance(value, float)
            assert value > previous_value

            previous_value = value

    @pytest.mark.integration
    def test_generate_freight_with_different_distances(self):
        origin_cep = "22041001"  # Av. Atlântica, Copacabana, Rio de Janeiro
        destination_ceps = [
            "20040030",  # Centro do Rio de Janeiro
            "01310200",  # São Paulo (média distância)
            "90010170",  # Porto Alegre (longa distância)
        ]

        weight = 2.0
        option = 1
        previous_value = 0

        for destination_cep in destination_ceps:
            result_str = generate_freight(
                weight=weight,
                option=option,
                origin_cep=origin_cep,
                destination_cep=destination_cep,
            )

            assert "The freight value is" in result_str

            value_str = result_str.split("is ")[-1]
            value = float(value_str)

            assert isinstance(value, float)
            assert value >= previous_value

            previous_value = value

    @pytest.mark.integration
    def test_brasil_api_provider_real_cep_data(self):
        provider = BrasilApiProvider()

        cep_data = provider.get_cep_data("22041001")

        assert "location" in cep_data
        assert "coordinates" in cep_data["location"]
        assert "latitude" in cep_data["location"]["coordinates"]
        assert "longitude" in cep_data["location"]["coordinates"]

        latitude = float(cep_data["location"]["coordinates"]["latitude"])
        longitude = float(cep_data["location"]["coordinates"]["longitude"])

        assert -90 <= latitude <= 90
        assert -180 <= longitude <= 180

    @pytest.mark.integration
    def test_invalid_option(self):
        origin_cep = "22041001"
        destination_cep = "01310200"
        weight = 5.0
        invalid_option = 4

        with pytest.raises(FreightTypeInvalidError):
            generate_freight(
                weight=weight,
                option=invalid_option,
                origin_cep=origin_cep,
                destination_cep=destination_cep,
            )

    @pytest.mark.integration
    def test_invalid_cep(self):
        origin_cep = "00000000"  # CEP inválido
        destination_cep = "01310200"
        weight = 5.0
        option = 2

        with pytest.raises(ExternalAPIError):
            generate_freight(
                weight=weight,
                option=option,
                origin_cep=origin_cep,
                destination_cep=destination_cep,
            )

    @pytest.mark.integration
    @patch("requests.get")
    def test_osrm_api_unavailable(self, mock_get):
        def side_effect_function(url, *args, **kwargs):
            from unittest.mock import MagicMock

            import requests

            if "brasilapi" in url:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "location": {
                        "coordinates": {
                            "latitude": -22.9723845,
                            "longitude": -43.1852774,
                        }
                    }
                }
                return mock_response
            else:
                raise requests.RequestException("OSRM API is unavailable")

        mock_get.side_effect = side_effect_function

        origin_cep = "22041001"
        destination_cep = "01310200"
        weight = 5.0
        option = 2

        with pytest.raises(
            ExternalAPIError, match="Failed to fetch distance from OSRM"
        ):
            generate_freight(
                weight=weight,
                option=option,
                origin_cep=origin_cep,
                destination_cep=destination_cep,
            )
