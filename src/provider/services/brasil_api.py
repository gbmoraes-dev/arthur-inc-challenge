import os
import requests
from dotenv import load_dotenv
from typing import Any, Dict

from provider.cep import CepProvider
from exceptions import ExternalAPIError, InvalidCepError


load_dotenv()


def has_valid_coordinates(data: Dict[str, Any]) -> bool:
    try:
        coordinates = data.get("location", {}).get("coordinates", {})

        if not (
            isinstance(coordinates, dict)
            and "latitude" in coordinates
            and "longitude" in coordinates
        ):
            return False

        lat = coordinates["latitude"]
        lon = coordinates["longitude"]

        if isinstance(lat, str):
            lat = float(lat)
        if isinstance(lon, str):
            lon = float(lon)

        if not (isinstance(lat, (int, float)) and isinstance(lon, (int, float))):
            return False

        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return False

        return True
    except (AttributeError, TypeError, ValueError):
        return False


class BrasilApiProvider(CepProvider):
    def get_cep_data(self, cep: str) -> Dict[str, Any]:
        base_url = os.getenv("BRASIL_API_URL")
        if not base_url:
            raise ValueError("BRASIL_API_URL not found in environment variables.")

        url = f"{base_url}{cep}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data: Dict[str, Any] = response.json()

            if not has_valid_coordinates(data):
                raise InvalidCepError(f"CEP {cep} não possui coordenadas válidas.")

            return data
        except requests.RequestException as e:
            raise ExternalAPIError(f"Failed to fetch CEP data: {str(e)}")
