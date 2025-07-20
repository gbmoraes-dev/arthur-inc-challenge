import os
import requests
from dotenv import load_dotenv
from exceptions import ExternalAPIError, InvalidCepError
from typing import Dict, Any

load_dotenv()

BRASIL_API_URL = os.getenv("BRASIL_API_URL")
OSRM_API_URL = os.getenv("OSRM_API_URL")


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


def get_cep_data(cep: str) -> dict:
    try:
        url = f"{BRASIL_API_URL}/{cep}"
        response = requests.get(url)
        response.raise_for_status()
        data: Dict[str, Any] = response.json()

        if not has_valid_coordinates(data):
            raise InvalidCepError(f"CEP {cep} not have valid coordinates.")

        return data
    except requests.RequestException as e:
        raise ExternalAPIError(f"Failed to fetch data for CEP {cep}: {str(e)}")


def get_distance_between_ceps(origin_cep: str, destination_cep: str) -> float:
    try:
        origin_data = get_cep_data(origin_cep)
        destination_data = get_cep_data(destination_cep)

        if not has_valid_coordinates(origin_data) or not has_valid_coordinates(
            destination_data
        ):
            raise InvalidCepError("Invalid CEP coordinates")

        origin_coords = origin_data["location"]["coordinates"]
        destination_coords = destination_data["location"]["coordinates"]

        lon1, lat1 = origin_coords["longitude"], origin_coords["latitude"]
        lon2, lat2 = destination_coords["longitude"], destination_coords["latitude"]

        url = f"{OSRM_API_URL}/{lon1},{lat1};{lon2},{lat2}"
        response = requests.get(url)
        response.raise_for_status()

        json_data = response.json()
        if not json_data.get("routes") or len(json_data["routes"]) == 0:
            raise ExternalAPIError("Distance not found in OSRM response.")

        distance_in_meters = json_data["routes"][0]["distance"]
        distance_in_km = distance_in_meters / 1000
        return distance_in_km
    except requests.RequestException as e:
        raise ExternalAPIError(f"Failed to fetch distance from OSRM: {str(e)}")
    except (KeyError, IndexError) as e:
        raise ExternalAPIError(f"Error parsing OSRM response: {str(e)}")
