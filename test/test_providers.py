import requests
from unittest.mock import MagicMock, patch

import pytest

from exceptions import ExternalAPIError, InvalidCepError
from provider.cep import CepProvider
from provider.services.brasil_api import BrasilApiProvider
from services import get_distance_between_ceps
from validation import Validation


class TestProviders:
    @patch("requests.get")
    def test_get_distance_between_ceps_handles_osrm_error(self, mock_get):
        mock_provider = MagicMock(spec=CepProvider)

        mock_provider.get_cep_data.return_value = {
            "location": {
                "coordinates": {"latitude": -22.9723845, "longitude": -43.1852774}
            }
        }

        mock_get.side_effect = requests.RequestException("OSRM API error")

        with pytest.raises(
            ExternalAPIError, match="Failed to fetch distance from OSRM: OSRM API error"
        ):
            get_distance_between_ceps("22041001", "01310200", mock_provider)

    @patch("requests.get")
    def test_get_distance_between_ceps_handles_invalid_osrm_response(self, mock_get):
        mock_provider = MagicMock(spec=CepProvider)

        mock_provider.get_cep_data.return_value = {
            "location": {
                "coordinates": {"latitude": -22.9723845, "longitude": -43.1852774}
            }
        }

        mock_response = MagicMock()
        mock_response.json.return_value = {"routes": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with pytest.raises(
            ExternalAPIError, match="Distance not found in OSRM response."
        ):
            get_distance_between_ceps("22041001", "01310200", mock_provider)


class TestBrasilApiProvider:
    @patch("requests.get")
    def test_brasil_api_provider_handles_request_exception(self, mock_get):
        mock_get.side_effect = requests.RequestException("Failed to connect")

        provider = BrasilApiProvider()

        with pytest.raises(
            ExternalAPIError, match="Failed to fetch CEP data: Failed to connect"
        ):
            provider.get_cep_data("01001000")

    @patch("requests.get")
    def test_brasil_api_provider_with_invalid_coordinates(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "location": {"coordinates": {"latitude": 100, "longitude": 200}}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = BrasilApiProvider()
        with pytest.raises(InvalidCepError, match="não possui coordenadas válidas"):
            provider.get_cep_data("12345678")

    def test_has_valid_coordinates_invalid_cases(self):
        invalid_cases = [
            {},
            {"location": {}},
            {"location": {"coordinates": {}}},
            {"location": {"coordinates": "not-a-dict"}},
            {"location": {"coordinates": {"longitude": -43.1}}},
            {"location": {"coordinates": {"latitude": -22.9}}},
            {"location": {"coordinates": {"latitude": "abc", "longitude": -43.1}}},
            {"location": {"coordinates": {"latitude": -22.9, "longitude": "xyz"}}},
            {"location": {"coordinates": {"latitude": 91, "longitude": -43.1}}},
            {"location": {"coordinates": {"latitude": -22.9, "longitude": 181}}},
        ]

        for case in invalid_cases:
            assert not Validation.has_valid_coordinates(case)

    def test_has_valid_coordinates_valid_cases(self):
        valid_cases = [
            {"location": {"coordinates": {"latitude": -22.9, "longitude": -43.1}}},
            {"location": {"coordinates": {"latitude": "-22.9", "longitude": "-43.1"}}},
            {"location": {"coordinates": {"latitude": 90, "longitude": 180}}},
            {"location": {"coordinates": {"latitude": -90, "longitude": -180}}},
        ]

        for case in valid_cases:
            assert Validation.has_valid_coordinates(case)
