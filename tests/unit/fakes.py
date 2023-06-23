from typing import Tuple

from air_bot.domain.repository import AbstractTicketRepo, AbstractUserDirectionRepo
from air_bot.domain.model import FlightDirection, FlightDirectionInfo, Ticket


class FakeTicketsApi(list):
    async def get_tickets(self, direction: FlightDirection, limit: int) -> list[Ticket]:
        return self


class FakeFlightDirectionRepo(list):
    async def get_direction_id(
        self, direction: FlightDirection
    ) -> Tuple[int | None, bool]:
        for direction_info in self:
            if direction_info.direction == direction:
                return direction_info.id, True
        return None, True

    async def add_direction_info(self, direction_info: FlightDirectionInfo):
        return None

    async def get_direction_info(
        self, direction: FlightDirection
    ) -> FlightDirectionInfo:
        return None


class FakeUserFlightDirectionRepo(AbstractUserDirectionRepo):
    def __init__(self, users_directions: list[Tuple[int, int]] = None):
        if users_directions is None:
            users_directions = []
        self.users_directions = users_directions

    async def add(self, user_id: int, direction_id: int):
        self.users_directions.append((user_id, direction_id))

    async def get_users_direction(self, user_id: int, direction: FlightDirection):
        return None


class FakeTicketRepo(AbstractTicketRepo):
    def __init__(self, tickets: list[Tuple[int, Ticket]] = None):
        if tickets is None:
            tickets = []
        self.ticket_rows = tickets

    async def add(self, direction_id: int, tickets: list[Ticket]) -> bool:
        for ticket in tickets:
            self.ticket_rows.append((direction_id, ticket))
        return True

    async def get_direction_tickets(self, direction_id: int) -> list[Ticket]:
        return [row[1] for row in self.ticket_rows if row[0] == direction_id]
