from typing import Optional

from model.freight import Freight
from services import get_distance_between_ceps


def generate_freight(
    weight: float,
    option: int,
    origin_cep: Optional[str] = None,
    destination_cep: Optional[str] = None,
    distance: Optional[float] = None,
) -> str:
    if origin_cep and destination_cep:
        distance = get_distance_between_ceps(origin_cep, destination_cep)

    if distance is None:
        raise ValueError("Distance or origin/destination CEPs must be provided.")

    freight = Freight(distance, weight)

    if option == 1:
        freight.type = "Normal"
    elif option == 2:
        freight.type = "Sedex"
    elif option == 3:
        freight.type = "Sedex10"
    else:
        raise ValueError("Invalid freight option.")

    freight.calculate_price()
    return f"The freight value is {freight.value:.2f}"


if __name__ == "__main__":
    weight = float(input("Enter the package weight -> "))
    origin_cep = input("Enter the origin CEP -> ")
    destination_cep = input("Enter the destination CEP -> ")
    option = int(
        input("Enter the delivery option\n\t(1)Normal\n\t(2)Sedex\n\t(3)Sedex10\n-> ")
    )
    print(
        generate_freight(
            weight=weight,
            option=option,
            origin_cep=origin_cep,
            destination_cep=destination_cep,
        )
    )
