from dataclasses import dataclass
from enum import Enum
from typing import Optional


class LocationType(Enum):
    AIRPORT = 1
    CITY = 2


@dataclass
class Location:
    type_: LocationType
    code: str
    name: str
    country_code: Optional[str]


@dataclass
class FlightDirection:
    start_code: str
    start_name: str
    end_code: str
    end_name: str
    with_transfer: bool
    departure_at: str
    return_at: Optional[str]

    def __hash__(self) -> int:
        result = hash(self.start_code)
        result = 31 * result + hash(self.end_code)
        result = 31 * result + hash(self.with_transfer)
        result = 31 * result + hash(self.departure_at)
        result = 31 * result + hash(self.return_at)
        return result


@dataclass
class FlightDirectionFull:
    id: int
    user_id: int
    direction: FlightDirection
