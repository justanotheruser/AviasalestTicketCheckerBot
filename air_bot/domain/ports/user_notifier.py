from abc import ABC, abstractmethod
from typing import List

from air_bot.domain.model import FlightDirection, Ticket


class UserNotifier(ABC):
    @abstractmethod
    async def notify_user(
        self,
        user_id: int,
        tickets: List[Ticket],
        direction: FlightDirection,
        direction_id: int,
    ):
        raise NotImplementedError
