import datetime
from abc import ABC, abstractmethod
from dataclasses import asdict

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from air_bot.adapters import orm
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


class SqlAlchemyFlightDirectionRepo(AbstractFlightDirectionRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def add_direction_info(
        self,
        direction: model.FlightDirection,
        price: float | None,
        last_update: datetime.datetime,
    ):
        stmt = text(
            "INSERT INTO flight_direction (start_code, start_name, end_code, end_name, "
            "with_transfer, departure_at, return_at, price, last_update) VALUES (:start_code, :start_name,"
            ":end_code, :end_name, :with_transfer, :departure_at, :return_at, :price, :last_update)"
        )
        stmt = stmt.bindparams(
            **asdict(direction), price=price, last_update=last_update
        )
        await self.session.execute(stmt)

    async def get_direction_id(self, direction: model.FlightDirection) -> int | None:
        """Returns id of row with direction info if exists or None otherwise"""
        stmt = select(model.FlightDirectionInfo).filter_by(
            start_code=direction.start_code,
            end_code=direction.end_code,
            with_transfer=direction.with_transfer,
            departure_at=direction.departure_at,
            return_at=direction.return_at,
        )
        result = await self.session.execute(stmt)
        row = result.first()
        if row is None:
            return None
        return row[0].id

    async def get_direction_info(
        self, direction: model.FlightDirection
    ) -> model.FlightDirectionInfo:
        stmt = select(model.FlightDirectionInfo)
        stmt.filter_by(
            start_code=direction.start_code,
            end_code=direction.end_code,
            with_transfer=direction.with_transfer,
            departure_at=direction.departure_at,
            return_at=direction.return_at,
        )
        result = await self.session.execute(stmt)
        return result.first()[0]


class SqlAlchemyUserDirectionRepo(AbstractUserDirectionRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def add(self, user_id: int, direction_id: int):
        stmt = text(
            "INSERT INTO users_directions (user_id, direction_id) VALUES (:user_id, :direction_id)"
        )
        stmt = stmt.bindparams(user_id=user_id, direction_id=direction_id)
        await self.session.execute(stmt)

    # TODO: figure out why we need it
    async def get_users_direction(self, user_id: int, direction_id: int):
        stmt = select(model.UserDirection).where(
            orm.users_directions_table.c.user_id == user_id
        )
        stmt = stmt.where(orm.users_directions_table.c.direction_id == direction_id)
        await self.session.execute(stmt)
