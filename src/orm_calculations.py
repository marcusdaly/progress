# from https://www.brianmac.co.uk/maxload.htm#:~:text=The%20Epley%20(1985)%20equation%20is,of%20repetitions%20%C3%97%20Weight)%20%2B%20Weight
# NOTE: Baechle and Epley are the same........

from typing import Literal

ORM_TYPE = Literal["Brzycki", "Epley", "Landers"]


def _calculate_brzycki_orm(total_weight: float, repetitions: int) -> float:
    return total_weight / (1.0278 - (0.0278 * repetitions))


def _calculate_epley_orm(total_weight: float, repetitions: int) -> float:
    return total_weight * (1 + (0.033 * repetitions))


def _calculate_landers_orm(total_weight: float, repetitions: int) -> float:
    return (100 * total_weight) / (101.3 - (2.67123 * repetitions))


def calculate_orm(
    added_weight: float,
    repetitions: int,
    bodyweight: float = 0.0,
    method: ORM_TYPE = "Epley",
) -> float:
    if method == "Brzycki":
        return (
            _calculate_brzycki_orm(
                total_weight=bodyweight + added_weight, repetitions=repetitions
            )
            - bodyweight
        )
    elif method == "Epley":
        return (
            _calculate_epley_orm(
                total_weight=bodyweight + added_weight, repetitions=repetitions
            )
            - bodyweight
        )
    elif method == "Landers":
        return (
            _calculate_landers_orm(
                total_weight=bodyweight + added_weight, repetitions=repetitions
            )
            - bodyweight
        )
    raise ValueError(method)
