from itertools import product
from typing import List

SECONDS_UNITS = ["s", "sec", "secs", "second", "seconds"]
MINUTES_UNITS = ["minute", "minutes", "min", "mins", "m", "ms"]
HOURS_UNITS = ["hour", "hours", "hr", "hrs", "h", "hs"]
POUNDS_UNITS = ["lb", "lbs"]
LEFT_UNITS = ["l", "left"]
RIGHT_UNITS = ["r", "right"]


def combine_units(units_1: List[str], units_2: List[str]) -> List[str]:
    return [" ".join(units) for units in product(units_1, units_2)]
