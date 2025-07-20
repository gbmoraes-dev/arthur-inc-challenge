import os
import requests
from dotenv import load_dotenv
from exceptions import ExternalAPIError
from typing import Any, Dict, List, cast
from provider.cep import CepProvider
from provider.services.brasil_api import has_valid_coordinates

load_dotenv()

BRASIL_API_URL = os.getenv("BRASIL_API_URL")
OSRM_API_URL = os.getenv("OSRM_API_URL")


def get_distance_between_ceps(
    origin_cep: str, destination_cep: str, cep_provider: CepProvider
) -> float:
    origin_data = cep_provider.get_cep_data(origin_cep)
    destination_data = cep_provider.get_cep_data(destination_cep)

    if not has_valid_coordinates(origin_data) or not has_valid_coordinates(
        destination_data
    ):
        raise ExternalAPIError(
            f"CEP de destino {destination_cep} não possui coordenadas válidas."
        )

    origin_coords = origin_data["location"]["coordinates"]
    destination_coords = destination_data["location"]["coordinates"]

    lon1, lat1 = origin_coords["longitude"], origin_coords["latitude"]
    lon2, lat2 = destination_coords["longitude"], destination_coords["latitude"]

    base_url = os.getenv("OSRM_API_URL")
    if not base_url:
        raise ValueError("OSRM_API_URL not found in environment variables.")

    url = f"{base_url}{lon1},{lat1};{lon2},{lat2}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        routes: List[Dict[str, Any]] = response.json().get("routes", [])
        if not routes or "distance" not in routes[0]:
            raise ExternalAPIError("Distance not found in OSRM response.")
        distance_in_meters = cast(float, routes[0]["distance"])
        distance_in_km = distance_in_meters / 1000
        return distance_in_km
    except requests.RequestException as e:
        raise ExternalAPIError(f"Failed to fetch distance from OSRM: {str(e)}")
