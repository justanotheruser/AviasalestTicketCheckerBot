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
    ) -> int:
        """Return id of inserted row"""
        raise NotImplementedError

    @abstractmethod
    async def get_direction_id(self, direction: model.FlightDirection) -> int | None:
        """Returns id of row with direction info if exists or None otherwise"""
        raise NotImplementedError

    @abstractmethod
    async def get_directions_info(
        self, direction_ids: list[int]
    ) -> list[model.FlightDirectionInfo]:
        raise NotImplementedError

    async def get_direction_info(self, direction_id: int) -> model.FlightDirectionInfo:
        directions = await self.get_directions_info([direction_id])
        return directions[0]

    @abstractmethod
    async def get_directions_with_last_update_before(
        self, last_update: datetime.datetime, limit: int
    ) -> list[model.FlightDirectionInfo]:
        raise NotImplementedError

    @abstractmethod
    async def update_price(
        self, direction_id: int, price: float, last_update: datetime.datetime
    ):
        raise NotImplementedError

    @abstractmethod
    async def delete_directions(self, direction_ids: list[int]):
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
    async def get_directions(self, user_id: int) -> list[int]:
        """Returns list of direction ids tracked by this user"""
        raise NotImplementedError

    @abstractmethod
    async def get_users(self, direction_id: int) -> list[int]:
        """Returns list of users that track this direction"""
        raise NotImplementedError

    @abstractmethod
    async def remove(self, user_id: int, direction_id: int):
        raise NotImplementedError


class AbstractTicketRepo(ABC):
    @abstractmethod
    async def add(self, tickets: list[model.Ticket], direction_id: int):
        raise NotImplementedError

    @abstractmethod
    async def get_direction_tickets(
        self, direction_id: int, limit: int | None = None
    ) -> list[model.Ticket]:
        raise NotImplementedError

    @abstractmethod
    async def remove_for_direction(self, direction_id: int):
        raise NotImplementedError
