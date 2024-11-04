import datetime
from abc import ABC, abstractmethod
from typing import List, Optional

from air_bot.domain import model


class FlightDirectionRepo(ABC):
    @abstractmethod
    async def add_direction_info(
        self,
        direction: model.FlightDirection,
        price: Optional[float],
        last_update: datetime.datetime,
    ) -> int:
        """Return id of inserted row"""
        raise NotImplementedError

    @abstractmethod
    async def get_direction_id(self, direction: model.FlightDirection) -> Optional[int]:
        """Returns id of row with direction info if exists or None otherwise"""
        raise NotImplementedError

    @abstractmethod
    async def get_directions_info(
        self, direction_ids: List[int]
    ) -> List[model.FlightDirectionInfo]:
        raise NotImplementedError

    async def get_direction_info(
        self, direction_id: int
    ) -> Optional[model.FlightDirectionInfo]:
        directions = await self.get_directions_info([direction_id])
        if directions:
            return directions[0]
        else:
            return None

    @abstractmethod
    async def get_directions_with_last_update_try_before(
        self, last_update: datetime.datetime, limit: int
    ) -> List[model.FlightDirectionInfo]:
        raise NotImplementedError

    @abstractmethod
    async def update_price(
        self, direction_id: int, price: Optional[float], last_update: datetime.datetime
    ):
        raise NotImplementedError

    @abstractmethod
    async def update_last_update_try(
        self, direction_id: int, last_update_try: datetime.datetime
    ):
        raise NotImplementedError

    @abstractmethod
    async def delete_direction(self, direction_id: int):
        raise NotImplementedError

    @abstractmethod
    async def delete_outdated_directions(self) -> int:
        """Returns number of deleted directions."""
        raise NotImplementedError


class UserRepo(ABC):
    @abstractmethod
    async def exists(self, user_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def add(self, user_id: int):
        raise NotImplementedError


class UserDirectionRepo(ABC):
    @abstractmethod
    async def add(self, user_id: int, direction_id: int):
        raise NotImplementedError

    @abstractmethod
    async def get_directions(self, user_id: int) -> List[int]:
        """Returns list of direction ids tracked by this user"""
        raise NotImplementedError

    @abstractmethod
    async def get_users(self, direction_id: int) -> List[int]:
        """Returns list of users that track this direction"""
        raise NotImplementedError

    @abstractmethod
    async def remove(self, user_id: int, direction_id: int):
        raise NotImplementedError


class TicketRepo(ABC):
    @abstractmethod
    async def add(self, tickets: List[model.Ticket], direction_id: int):
        raise NotImplementedError

    @abstractmethod
    async def get_direction_tickets(
        self, direction_id: int, limit: Optional[int] = None
    ) -> List[model.Ticket]:
        raise NotImplementedError

    @abstractmethod
    async def remove_for_direction(self, direction_id: int):
        raise NotImplementedError
