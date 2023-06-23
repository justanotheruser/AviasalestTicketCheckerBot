import datetime
from abc import ABC, abstractmethod

from air_bot.domain import model


class AbstractFlightDirectionRepo(ABC):
    @abstractmethod
    async def add_direction_info(
        self,
        direction: model.FlightDirection,
        price: float | None,
        last_update: datetime.datetime,
    ):
        raise NotImplementedError

    @abstractmethod
    async def get_direction_id(self, direction: model.FlightDirection) -> int | None:
        """Returns id of row with direction info if exists or None otherwise"""
        raise NotImplementedError

    @abstractmethod
    async def get_direction_info(
        self, direction: model.FlightDirection
    ) -> model.FlightDirectionInfo:
        raise NotImplementedError


class AbstractUserRepo(ABC):
    @abstractmethod
    async def add(self, user_id: int):
        raise NotImplementedError


class AbstractUserDirectionRepo(ABC):
    @abstractmethod
    async def add(self, user_id: int, direction_id: int):
        raise NotImplementedError

    @abstractmethod
    async def get_users_direction(self, user_id: int, direction: model.FlightDirection):
        raise NotImplementedError


class AbstractTicketRepo(ABC):
    @abstractmethod
    async def add(self, direction_id: int, tickets: list[model.Ticket]) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_direction_tickets(self, direction_id: int) -> list[model.Ticket]:
        raise NotImplementedError