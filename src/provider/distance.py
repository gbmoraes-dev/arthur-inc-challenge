from abc import ABC, abstractmethod


class DistanceProvider(ABC):
    @abstractmethod
    def get_distance(
        self, origin_lon: float, origin_lat: float, dest_lon: float, dest_lat: float
    ) -> float:
        pass
