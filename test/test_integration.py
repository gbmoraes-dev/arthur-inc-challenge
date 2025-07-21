import pytest

from exceptions import FreightTypeInvalidError
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
