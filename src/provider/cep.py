from abc import ABC, abstractmethod


class CepProvider(ABC):
    @abstractmethod
    def get_cep_data(self, cep: str) -> dict:
        pass
