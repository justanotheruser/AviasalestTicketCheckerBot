import datetime
from dataclasses import asdict

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from air_bot.adapters.repo import orm
from air_bot.domain import model
from air_bot.domain.repository import AbstractFlightDirectionRepo


class SqlAlchemyFlightDirectionRepo(AbstractFlightDirectionRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def add_direction_info(
        self,
        direction: model.FlightDirection,
        price: float | None,
        last_update: datetime.datetime,
    ) -> int:
        stmt = text(
            "INSERT INTO flight_directions (start_code, start_name, end_code, end_name, "
            "with_transfer, departure_at, return_at, price, last_update) VALUES (:start_code, :start_name,"
            ":end_code, :end_name, :with_transfer, :departure_at, :return_at, :price, :last_update)"
        )
        stmt = stmt.bindparams(
            **asdict(direction), price=price, last_update=last_update
        )
        result = await self.session.execute(stmt)
        return result.lastrowid

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

    async def get_directions_info(
        self, direction_ids: list[int]
    ) -> list[model.FlightDirectionInfo]:
        stmt = select(model.FlightDirectionInfo)
        stmt = stmt.where(orm.flight_direction_info_table.c.id.in_(direction_ids))
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]

    async def delete_directions(self, direction_ids: list[int]):
        stmt = delete(model.FlightDirectionInfo)
        stmt = stmt.where(orm.flight_direction_info_table.c.id.in_(direction_ids))
        await self.session.execute(stmt)
