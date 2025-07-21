import unittest
from unittest.mock import patch, Mock
import requests
import pybreaker
from typing import Callable

from provider.services.brasil_api import BrasilApiProvider
from provider.services.osrm_api import OSRMProvider
from provider.resilience import brasil_api_breaker, osrm_api_breaker
from exceptions import ExternalAPIError


def mock_with_retry(*args, **kwargs) -> Callable[[Callable], Callable]:
    def decorator(func: Callable) -> Callable:
        return func

    return decorator


class TestResiliencePatterns(unittest.TestCase):
    def reset_breakers(self):
        brasil_api_breaker.close()
        osrm_api_breaker.close()

    def setUp(self):
        self.reset_breakers()

        self.valid_cep_data = {
            "location": {
                "coordinates": {
                    "longitude": -43.2096,
                    "latitude": -22.9035,
                }
            }
        }

    @patch("requests.get")
    @patch("provider.services.brasil_api.brasil_api_breaker", lambda f: f)
    @patch("provider.services.brasil_api.with_retry", mock_with_retry)
    def test_brasil_api_retry(self, mock_requests_get):
        mock_response_success = Mock()
        mock_response_success.json.return_value = self.valid_cep_data
        mock_response_success.raise_for_status.return_value = None

        mock_requests_get.side_effect = [
            requests.exceptions.ConnectionError("Connection refused"),
            requests.exceptions.ConnectionError("Connection refused"),
            mock_response_success,
        ]

        with patch(
            "provider.resilience.retry", side_effect=lambda *args, **kwargs: lambda f: f
        ):
            provider = BrasilApiProvider()

            with self.assertRaises(ExternalAPIError):
                provider.get_cep_data("12345678")

            with self.assertRaises(ExternalAPIError):
                provider.get_cep_data("12345678")

            result = provider.get_cep_data("12345678")
            self.assertEqual(result, self.valid_cep_data)

            self.assertEqual(mock_requests_get.call_count, 3)

    @patch("requests.get")
    @patch("provider.services.osrm_api.osrm_api_breaker", lambda f: f)
    @patch("provider.services.osrm_api.with_retry", mock_with_retry)
    def test_osrm_api_retry(self, mock_requests_get):
        mock_response_success = Mock()
        mock_response_success.json.return_value = {"routes": [{"distance": 15000}]}
        mock_response_success.raise_for_status.return_value = None

        mock_requests_get.side_effect = [
            requests.exceptions.ConnectionError("Connection refused"),
            requests.exceptions.ConnectionError("Connection refused"),
            mock_response_success,
        ]

        with patch(
            "provider.resilience.retry", side_effect=lambda *args, **kwargs: lambda f: f
        ):
            provider = OSRMProvider()

            with self.assertRaises(ExternalAPIError):
                provider.get_distance(0, 0, 1, 1)

            with self.assertRaises(ExternalAPIError):
                provider.get_distance(0, 0, 1, 1)

            distance = provider.get_distance(0, 0, 1, 1)
            self.assertEqual(distance, 15)  # 15000m = 15km

            self.assertEqual(mock_requests_get.call_count, 3)

    @patch("requests.get")
    def test_circuit_breaker_opens_after_failures(self, mock_requests_get):
        mock_requests_get.side_effect = requests.exceptions.ConnectionError(
            "Connection refused"
        )

        with patch(
            "provider.resilience.with_retry", lambda *args, **kwargs: lambda f: f
        ):
            provider = BrasilApiProvider()

            for _ in range(3):
                try:
                    provider.get_cep_data("12345678")
                except (ExternalAPIError, pybreaker.CircuitBreakerError):
                    pass

            with self.assertRaises(pybreaker.CircuitBreakerError):
                provider.get_cep_data("12345678")
