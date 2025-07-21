import requests
import pytest
from unittest.mock import MagicMock, patch

from exceptions import ExternalAPIError
from provider.cep import CepProvider
from services import get_distance_between_ceps


class TestServices:
    @patch("requests.get")
    @patch("provider.resilience.osrm_api_breaker", lambda f: f)
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
    @patch("provider.resilience.osrm_api_breaker", lambda f: f)
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
