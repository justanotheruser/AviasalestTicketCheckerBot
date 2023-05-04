import configparser
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("AirBot")


class Interval(Enum):
    SECONDS = 0
    MINUTES = 1


@dataclass
class Config:
    check_interval: int
    check_interval_units: Interval
    price_reduction_threshold_percents: int


def read_config(filepath: str) -> Config:
    raw_config = configparser.ConfigParser()
    try:
        if not raw_config.read(filepath, encoding="utf-8"):
            raise RuntimeError(f"Can't read ticker price checker config {filepath}")
        check_interval_units_str = raw_config["settings"]["check_interval_units"]
        if check_interval_units_str == "seconds":
            check_interval_units = Interval.SECONDS
        elif check_interval_units_str == "minutes":
            check_interval_units = Interval.MINUTES
        else:
            raise RuntimeError(
                f"Unknown check_interval_units value '{check_interval_units_str}'"
            )
        return Config(
            check_interval=int(raw_config["settings"]["check_interval"]),
            check_interval_units=check_interval_units,
            price_reduction_threshold_percents=int(
                raw_config["settings"]["price_reduction_threshold_percents"]
            ),
        )
    except Exception as ex:
        raise RuntimeError(
            f"Failed to read ticker price checker config {filepath}: {ex}"
        )
