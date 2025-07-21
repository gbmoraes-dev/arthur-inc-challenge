import os
import requests
from dotenv import load_dotenv
from typing import Any, Dict

from provider.cep import CepProvider
from provider.resilience import brasil_api_breaker, with_retry
from provider.cache import cached
from exceptions import ExternalAPIError, InvalidCepError
from validation import Validation

load_dotenv()


class BrasilApiProvider(CepProvider):
    def __init__(self):
        self._base_url = os.getenv("BRASIL_API_URL")
        if not self._base_url:
            raise ValueError("BRASIL_API_URL not found in environment variables.")

    @cached(prefix="brasil_api", expiry=86400)  # Cache por 24 horas
    @with_retry(max_attempts=3, min_wait=1.0, max_wait=5.0)
    @brasil_api_breaker
    def get_cep_data(self, cep: str) -> Dict[str, Any]:
        if not Validation.is_valid_cep(cep):
            raise InvalidCepError(f"CEP {cep} inválido.")

        url = f"{self._base_url}{cep}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data: Dict[str, Any] = response.json()

            if not Validation.has_valid_coordinates(data):
                raise InvalidCepError(f"CEP {cep} not have valid coordinates.")

            return data
        except requests.RequestException as e:
            raise ExternalAPIError(f"Failed to fetch CEP data: {str(e)}")
