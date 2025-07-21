import os
from typing import Dict, Any, List, cast
import requests
from dotenv import load_dotenv

from exceptions import ExternalAPIError
from provider.distance import DistanceProvider
from provider.resilience import osrm_api_breaker, with_retry

load_dotenv()


class OSRMProvider(DistanceProvider):
    def __init__(self):
        self._api_url = os.getenv("OSRM_API_URL")
        if not self._api_url:
            raise ValueError("OSRM_API_URL not found in environment variables.")

    @with_retry(max_attempts=3, min_wait=1.0, max_wait=5.0)
    @osrm_api_breaker
    def get_distance(
        self, origin_lon: float, origin_lat: float, dest_lon: float, dest_lat: float
    ) -> float:
        url = f"{self._api_url}{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
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
