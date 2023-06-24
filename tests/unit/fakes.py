import datetime
from typing import Tuple
from dataclasses import asdict

from air_bot.domain import repository
from air_bot.domain import model
from air_bot.adapters.repo.uow import AbstractUnitOfWork


class FakeTicketsApi(list):
    async def get_tickets(self, direction: model.FlightDirection, limit: int) -> list[model.Ticket]:
        return self


class FakeUserRepo(repository.AbstractUserRepo):
    def __init__(self, users: list[model.User] = None):
        if users is None:
            users = []
        self.users = users

    async def add(self, user_id: int):
        self.users.append(model.User(user_id=user_id))


class FakeFlightDirectionRepo(repository.AbstractFlightDirectionRepo):
    def __init__(self):
        self._next_id = 0
        self.directions: list[model.FlightDirectionInfo] = []

    async def add_direction_info(
        self,
        direction: model.FlightDirection,
        price: float | None,
        last_update: datetime.datetime,
    ):

        self.directions.append(model.FlightDirectionInfo(id=self._next_id, **asdict(direction),
                                              price=price, last_update=last_update))
        row_id = self._next_id
        self._next_id += 1
        return row_id

    async def get_direction_id(self, direction: model.FlightDirection) -> int | None:
        for direction_info in self.directions:
            if direction_info.direction == direction:
                return direction_info.id
        return None

    async def get_direction_info(
        self, direction: model.FlightDirection
    ) -> model.FlightDirectionInfo:
        for direction_info in self.directions:
            if direction_info.direction == direction:
                return direction_info
        return None


class FakeUserFlightDirectionRepo(repository.AbstractUserDirectionRepo):
    def __init__(self, users_directions: list[Tuple[int, int]] = None):
        if users_directions is None:
            users_directions = []
        self.users_directions = users_directions

    async def add(self, user_id: int, direction_id: int):
        self.users_directions.append((user_id, direction_id))

    async def get_user_directions(self, user_id: int, direction: model.FlightDirection):
        return None


class FakeTicketRepo(repository.AbstractTicketRepo):
    def __init__(self, tickets: list[Tuple[int, model.Ticket]] = None):
        if tickets is None:
            tickets = []
        self.ticket_rows = tickets

    async def add(self, direction_id: int, tickets: list[model.Ticket]) -> bool:
        for ticket in tickets:
            self.ticket_rows.append((direction_id, ticket))
        return True

    async def get_direction_tickets(self, direction_id: int) -> list[model.Ticket]:
        return [row[1] for row in self.ticket_rows if row[0] == direction_id]


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        super().__init__(None)
        self.users = FakeUserRepo()
        self.flight_directions = FakeFlightDirectionRepo()
        self.users_directions = FakeUserFlightDirectionRepo()
        self.tickets = FakeTicketRepo()

    async def _commit(self):
        pass

    async def _rollback(self):
        pass
