import datetime
from dataclasses import asdict
from typing import List, Optional

from sqlalchemy import delete, insert, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from air_bot.adapters.repo import orm
from air_bot.domain import model
from air_bot.domain.ports.repository import FlightDirectionRepo


class SqlAlchemyFlightDirectionRepo(FlightDirectionRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def add_direction_info(
        self,
        direction: model.FlightDirection,
        price: Optional[float],
        last_update: datetime.datetime,
    ) -> int:
        stmt = text(
            "INSERT INTO flight_directions (start_code, start_name, end_code, end_name, "
            "with_transfer, departure_at, return_at, price, last_update, last_update_try) VALUES (:start_code, "
            ":start_name, :end_code, :end_name, :with_transfer, :departure_at, :return_at, :price, :last_update, "
            ":last_update)"
        )
        stmt = stmt.bindparams(
            **asdict(direction), price=price, last_update=last_update
        )
        result = await self.session.execute(stmt)
        return result.lastrowid  # type: ignore[attr-defined]

    async def get_direction_id(self, direction: model.FlightDirection) -> Optional[int]:
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
        self, direction_ids: List[int]
    ) -> List[model.FlightDirectionInfo]:
        stmt = select(model.FlightDirectionInfo)
        stmt = stmt.where(orm.flight_direction_info_table.c.id.in_(direction_ids))
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]

    async def get_directions_with_last_update_try_before(
        self, last_update_try: datetime.datetime, limit: int
    ) -> List[model.FlightDirectionInfo]:
        stmt = (
            select(model.FlightDirectionInfo)
            .where(orm.flight_direction_info_table.c.last_update_try < last_update_try)
            .order_by(orm.flight_direction_info_table.c.last_update)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]

    async def update_price(
        self, direction_id: int, price: Optional[float], last_update: datetime.datetime
    ):
        stmt = (
            update(model.FlightDirectionInfo)
            .where(orm.flight_direction_info_table.c.id == direction_id)
            .values(price=price, last_update=last_update, last_update_try=last_update)
        )
        await self.session.execute(stmt)

    async def update_last_update_try(
        self, direction_id: int, last_update_try: datetime.datetime
    ):
        stmt = (
            update(model.FlightDirectionInfo)
            .where(orm.flight_direction_info_table.c.id == direction_id)
            .values(last_update_try=last_update_try)
        )
        await self.session.execute(stmt)

    async def delete_direction(self, direction_id: int):
        stmt = select(model.FlightDirectionInfo)
        stmt = stmt.where(orm.flight_direction_info_table.c.id == direction_id)
        result = await self.session.execute(stmt)
        row = result.first()
        if row is None:
            return

        direction_info: model.FlightDirectionInfo = row[0]
        now = datetime.datetime.now()
        historic_direction = model.HistoricFlightDirection(
            start_code=direction_info.start_code,
            start_name=direction_info.start_name,
            end_code=direction_info.end_code,
            end_name=direction_info.end_name,
            with_transfer=direction_info.with_transfer,
            departure_at=direction_info.departure_at,
            return_at=direction_info.return_at,
            price=direction_info.price,
            last_update=direction_info.last_update,
            deleted_at=now,
            deleted_by_user=True,
        )
        stmt = insert(model.HistoricFlightDirection).values(  # type: ignore[assignment]
            **asdict(historic_direction)
        )
        await self.session.execute(stmt)

        stmt = delete(model.FlightDirectionInfo)  # type: ignore[assignment]
        stmt = stmt.where(orm.flight_direction_info_table.c.id == direction_id)
        await self.session.execute(stmt)

    async def delete_outdated_directions(self) -> int:
        # Subtract one day, so we are sure direction is outdated in every time zone
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        year_month = datetime.datetime.strftime(yesterday, "%Y-%m")
        year_month_day = datetime.datetime.strftime(yesterday, "%Y-%m-%d")
        stmt = text(
            "SELECT * FROM flight_directions "
            "WHERE (LENGTH(departure_at) = 10 AND departure_at < :year_month_day) OR"
            " (LENGTH(departure_at) = 7 AND departure_at < :year_month);"
        )
        stmt = stmt.bindparams(year_month_day=year_month_day, year_month=year_month)
        result = await self.session.execute(stmt)
        outdated_directions = result.all()
        if not outdated_directions:
            return 0

        now = datetime.datetime.now()
        for row in outdated_directions:
            historic_direction = model.HistoricFlightDirection(
                start_code=row[1],
                start_name=row[2],
                end_code=row[3],
                end_name=row[4],
                with_transfer=row[5],
                departure_at=row[6],
                return_at=row[7],
                price=row[8],
                last_update=row[9],
                deleted_at=now,
                deleted_by_user=False,
            )
            stmt = insert(model.HistoricFlightDirection).values(  # type: ignore[assignment]
                **asdict(historic_direction)
            )
            await self.session.execute(stmt)

        outdated_directions_ids = [row[0] for row in outdated_directions]
        stmt = delete(model.FlightDirectionInfo)  # type: ignore[assignment]
        stmt = stmt.where(  # type: ignore[attr-defined]
            orm.flight_direction_info_table.c.id.in_(outdated_directions_ids)
        )
        await self.session.execute(stmt)
        return len(outdated_directions)
