import datetime
from dataclasses import asdict
from typing import Tuple

from air_bot.adapters.repo.uow import AbstractUnitOfWork
from air_bot.domain import model, repository


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
    ) -> int:
        self.directions.append(
            model.FlightDirectionInfo(
                id=self._next_id,
                **asdict(direction),
                price=price,
                last_update=last_update
            )
        )
        row_id = self._next_id
        self._next_id += 1
        return row_id

    async def get_direction_id(self, direction: model.FlightDirection) -> int | None:
        for direction_info in self.directions:
            if direction_info.direction == direction:
                return direction_info.id
        return None

    async def get_directions_info(
        self, direction_ids: list[int]
    ) -> list[model.FlightDirectionInfo]:
        result = []
        for direction_info in self.directions:
            if direction_info.id in direction_ids:
                result.append(direction_info)
        return result

    async def get_directions_with_last_update_before(
        self, last_update: datetime.datetime, limit: int
    ) -> list[model.FlightDirectionInfo]:
        sorted_directions = sorted(
            self.directions, key=lambda direction: direction.last_update
        )
        return sorted_directions[: min(limit, len(sorted_directions))]

    async def update_price(
        self, direction_id: int, price: float, last_update: datetime.datetime
    ):
        for i in range(len(self.directions)):
            if self.directions[i].id == direction_id:
                self.directions[i].price = price
                self.directions[i].last_update = last_update

    async def delete_directions(self, direction_ids: list[int]):
        self.directions = [
            direction_info
            for direction_info in self.directions
            if direction_info.id not in direction_ids
        ]


class FakeUserFlightDirectionRepo(repository.AbstractUserDirectionRepo):
    def __init__(self, users_directions: list[Tuple[int, int]] = None):
        if users_directions is None:
            users_directions = []
        self.users_directions = users_directions

    async def add(self, user_id: int, direction_id: int):
        self.users_directions.append((user_id, direction_id))

    async def get_directions(self, user_id: int):
        return [ud[1] for ud in self.users_directions if ud[0] == user_id]

    async def get_users(self, direction_id: int) -> list[int]:
        return [ud[0] for ud in self.users_directions if ud[1] == direction_id]


class FakeTicketRepo(repository.AbstractTicketRepo):
    def __init__(self, tickets: list[Tuple[model.Ticket, int]] = None):
        if tickets is None:
            tickets = []
        self.ticket_rows = tickets

    async def add(self, tickets: list[model.Ticket], direction_id: int) -> bool:
        for ticket in tickets:
            self.ticket_rows.append((ticket, direction_id))
        return True

    async def get_direction_tickets(self, direction_id: int) -> list[model.Ticket]:
        return [row[0] for row in self.ticket_rows if row[1] == direction_id]

    async def remove_for_direction(self, direction_id: int):
        self.ticket_rows = [row for row in self.ticket_rows if row[1] != direction_id]


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
