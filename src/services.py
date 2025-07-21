from dotenv import load_dotenv
from exceptions import ExternalAPIError
from provider.cep import CepProvider
from provider.services.osrm_api import OSRMProvider
from validation import Validation
from provider.resilience import with_retry

load_dotenv()


@with_retry(max_attempts=2, min_wait=1.0, max_wait=3.0)
def get_distance_between_ceps(
    origin_cep: str, destination_cep: str, cep_provider: CepProvider
) -> float:
    origin_data = cep_provider.get_cep_data(origin_cep)
    destination_data = cep_provider.get_cep_data(destination_cep)

    if not Validation.has_valid_coordinates(
        origin_data
    ) or not Validation.has_valid_coordinates(destination_data):
        raise ExternalAPIError(f"CEP {origin_cep} or {destination_cep} is invalid.")

    origin_coords = origin_data["location"]["coordinates"]
    destination_coords = destination_data["location"]["coordinates"]

    lon1, lat1 = origin_coords["longitude"], origin_coords["latitude"]
    lon2, lat2 = destination_coords["longitude"], destination_coords["latitude"]

    distance_provider = OSRMProvider()
    return distance_provider.get_distance(lon1, lat1, lon2, lat2)
