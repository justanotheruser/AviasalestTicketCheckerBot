import datetime
from dataclasses import dataclass
from functools import cached_property
from typing import Optional


@dataclass(frozen=True)
class FlightDirection:
    start_code: str
    start_name: str
    end_code: str
    end_name: str
    with_transfer: bool
    departure_at: str
    return_at: Optional[str] = None

    def departure_date(self) -> datetime.date:
        if len(self.departure_at) == 7:
            return datetime.datetime.strptime(self.departure_at, "%Y-%m")
        return datetime.datetime.strptime(self.departure_at, "%Y-%m-%d")

    def return_date(self) -> Optional[datetime.date]:
        if not self.return_at:
            return None
        if len(self.return_at) == 7:
            return datetime.datetime.strptime(self.return_at, "%Y-%m")
        return datetime.datetime.strptime(self.return_at, "%Y-%m-%d")


@dataclass
class FlightDirectionInfo:
    start_code: str
    start_name: str
    end_code: str
    end_name: str
    with_transfer: bool
    departure_at: str
    return_at: Optional[str]
    price: Optional[float]
    last_update: datetime.datetime
    last_update_try: datetime.datetime
    id: Optional[int] = None

    @cached_property
    def direction(self):
        return FlightDirection(
            start_code=self.start_code,
            start_name=self.start_name,
            end_code=self.end_code,
            end_name=self.end_name,
            with_transfer=self.with_transfer,
            departure_at=self.departure_at,
            return_at=self.return_at,
        )


@dataclass
class User:
    user_id: int


@dataclass(frozen=True)
class Ticket:
    price: float
    departure_at: datetime.datetime
    duration_to: datetime.timedelta
    link: str
    return_at: Optional[datetime.datetime] = None
    duration_back: Optional[datetime.timedelta] = None


@dataclass(frozen=True)
class Location:
    code: str
    name: str
    country_code: Optional[str]


@dataclass
class HistoricFlightDirection:
    start_code: str
    start_name: str
    end_code: str
    end_name: str
    with_transfer: bool
    departure_at: str
    return_at: Optional[str]
    price: Optional[float]
    last_update: datetime.datetime
    deleted_at: datetime.datetime
    deleted_by_user: bool
    id: Optional[int] = None
