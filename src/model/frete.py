class Frete:
    _tipo: str
    _valor: float

    def __init__(self, distancia, peso):
        self._distancia = distancia
        self._peso = peso

    # Getters
    @property
    def tipo(self) -> str:
        return self._tipo

    @property
    def valor(self) -> float:
        return self._valor

    @property
    def distancia(self) -> float:
        return self._distancia

    @property
    def peso(self) -> float:
        return self._peso

    # Setters
    @tipo.setter
    def tipo(self, tipo: str) -> None:
        self._tipo = tipo

    @valor.setter
    def valor(self, valor: float) -> None:
        self._valor = valor

    @distancia.setter
    def distancia(self, distancia: float) -> None:
        self._distancia = distancia

    @peso.setter
    def peso(self, peso: float) -> None:
        self._peso = peso

    def calcular_preco(self) -> float:
        if "Nromal" == self._tipo:
            self._valor = self._distancia * self._peso + 5
        elif "Sedex" == self._tipo:
            self._valor = self._distancia * self._peso + 10
        elif "Sedex10" == self._tipo:
            self._valor = self._distancia * self._peso + 15
