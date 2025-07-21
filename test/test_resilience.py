import unittest
from unittest.mock import patch, Mock
import requests
import pybreaker

from provider.services.brasil_api import BrasilApiProvider
from exceptions import ExternalAPIError


def mock_with_retry(*args, **kwargs):
    def decorator(func):
        return func

    return decorator


class TestResiliencePatterns(unittest.TestCase):
    def setUp(self):
        from provider.resilience import brasil_api_breaker

        brasil_api_breaker.close()

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
    def test_retry_pattern(self, mock_requests_get):
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
    def test_circuit_breaker_pattern(self, mock_requests_get):
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
