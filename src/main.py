from typing import Optional

from exceptions import (
    DistanceInvalidError,
    FreightError,
    FreightTypeInvalidError,
)
from model.freight import Freight
from provider.services.brasil_api import BrasilApiProvider
from services import get_distance_between_ceps
from factories.freight_factory import FreightStrategyFactory


def generate_freight(
    weight: float,
    option: int,
    origin_cep: Optional[str] = None,
    destination_cep: Optional[str] = None,
    distance: Optional[float] = None,
) -> str:
    if origin_cep and destination_cep:
        brasil_api_provider = BrasilApiProvider()
        distance = get_distance_between_ceps(
            origin_cep, destination_cep, brasil_api_provider
        )

    if distance is None:
        raise DistanceInvalidError(
            "Distance or origin/destination CEPs must be provided."
        )

    factory = FreightStrategyFactory()

    try:
        strategy = factory.create_strategy(option)
    except FreightTypeInvalidError:
        raise FreightTypeInvalidError("Invalid freight option.")

    freight = Freight(distance, weight, strategy)

    return f"The freight value is {freight.value:.2f}"


def main():
    try:
        weight = float(input("Enter the package weight -> "))
        origin_cep = input("Enter the origin CEP -> ")
        destination_cep = input("Enter the destination CEP -> ")
        option = int(
            input(
                "Enter the delivery option\n\t(1)Normal\n\t(2)Sedex\n\t(3)Sedex10\n-> "
            )
        )
        print(
            generate_freight(
                weight=weight,
                option=option,
                origin_cep=origin_cep,
                destination_cep=destination_cep,
            )
        )
    except (FreightError, ValueError) as e:
        print(f"Error: {str(e)}")
    except Exception:
        print("Unexpected internal error. Please try again later.")


if __name__ == "__main__":
    main()
