import logging
import typing
from contextlib import contextmanager
from typing import Optional, Any
import asyncio

from air_bot.bot_types import FlightDirectionFull, FlightDirection
from air_bot.config import BotConfig
from sqlalchemy.ext.asyncio import create_async_engine

from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import Integer, String, Boolean
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.asyncio import async_sessionmaker
from air_bot.db.mapping import Base, UserFlightDirection
from sqlalchemy import select, delete

logger = logging.getLogger(__name__)


class DBManager:
    def __init__(self, config: BotConfig):
        username = config.db_user
        password = config.db_pass.get_secret_value()
        host = config.db_host
        dbname = config.db_name
        self.engine = create_async_engine(
            f"mysql+asyncmy://{username}:{password}@{host}/{dbname}",
            echo=True,
        )

    async def start(self):
        logger.info(f'DBManager: starting')
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info(f'DBManager: started')
        '''user_id = 1
        direction = FlightDirection(start_code='ABC', start_name='bbbbAggggggA', end_code='DEF', end_name='BBBBB',
                               with_transfer=True, departure_at='2023-06-01', return_at=None)
        await self.save_or_update_flight_direction(user_id, direction, price=None)
        print(await self.delete_users_flight_direction(user_id, 65))'''

    async def stop(self):
        logger.info(f'DBManager: stopping')
        await self.engine.dispose()
        logger.info(f'DBManager: stopped')

    async def save_or_update_flight_direction(self, user_id: int, direction: FlightDirection, price: int) -> Optional[int]:
        async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        async with async_session() as session:
            async with session.begin():
                stmt = select(UserFlightDirection)
                stmt = where_flight_direction_and_user(stmt, direction, user_id)
                stmt_result = await session.scalars(stmt)
                existing_direction = stmt_result.first()  # type: Optional[UserFlightDirection]
                if existing_direction:
                    existing_direction.price = price
                    return existing_direction.id

                new_direction = UserFlightDirection(user_id=user_id, start_code=direction.start_code,
                    start_name=direction.start_name, end_code=direction.end_code,
                    end_name=direction.end_name, price=price, with_transfer=direction.with_transfer,
                    departure_at=direction.departure_at, return_at=direction.return_at)
                try:
                    session.add(new_direction)
                    await session.flush()
                    await session.refresh(new_direction)
                    return new_direction.id
                except Exception as e:
                    logger.error(f"DatabaseError {e}")
                    return None

    async def update_flight_direction_price(
        self, user_id: int, direction: FlightDirection, price: int
    ) -> None:
        async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        async with async_session() as session:
            async with session.begin():
                stmt = select(UserFlightDirection)
                stmt = where_flight_direction_and_user(stmt, direction, user_id)
                stmt_result = await session.scalars(stmt)
                users_direction = stmt_result.one()
                users_direction.price = price

    async def get_price(self, user_id: int, direction: FlightDirection) -> Optional[int]:
        async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        async with async_session() as session:
            async with session.begin():
                stmt = select(UserFlightDirection.price)
                stmt = where_flight_direction_and_user(stmt, direction, user_id)
                stmt_result = await session.scalars(stmt)
                return stmt_result.one()

    async def get_users_flight_directions(self, user_id: int) -> list[UserFlightDirection]:
        async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        async with async_session() as session:
            async with session.begin():
                stmt = select(UserFlightDirection).where(UserFlightDirection.user_id == user_id)
                stmt_result = await session.scalars(stmt)
                return stmt_result.all()

    async def get_users_flight_direction(self, user_id: int, direction_id: int) -> UserFlightDirection:
        async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        async with async_session() as session:
            async with session.begin():
                stmt = (select(UserFlightDirection)
                        .where(UserFlightDirection.user_id == user_id)
                        .where(UserFlightDirection.id == direction_id)
                        )
                stmt_result = await session.scalars(stmt)
                return stmt_result.first()

    async def delete_users_flight_direction(self, user_id: int, direction_id: int) -> None:
        async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        async with async_session() as session:
            async with session.begin():
                stmt = (delete(UserFlightDirection)
                        .where(UserFlightDirection.user_id == user_id)
                        .where(UserFlightDirection.id == direction_id)
                        )
                result = await session.execute(stmt)
                if result.rowcount == 0:
                    logger.warning(f"Attempt to delete non existing direction for user {user_id}, direction id {direction_id}")


def where_flight_direction_and_user(stmt, direction: FlightDirection, user_id: int):
    return (stmt.where(UserFlightDirection.user_id == user_id)
                    .where(UserFlightDirection.start_code == direction.start_code)
                    .where(UserFlightDirection.start_name == direction.start_name)
                    .where(UserFlightDirection.end_code == direction.end_code)
                    .where(UserFlightDirection.end_name == direction.end_name)
                    .where(UserFlightDirection.with_transfer == direction.with_transfer)
                    .where(UserFlightDirection.departure_at == direction.departure_at)
                    .where(UserFlightDirection.return_at == direction.return_at))
