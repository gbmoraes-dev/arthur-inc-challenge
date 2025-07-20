from typing import Any, Dict


class Validation:
    @staticmethod
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
