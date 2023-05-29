import logging
from typing import Optional, Sequence, Tuple

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from air_bot.bot_types import FlightDirection
from air_bot.config import BotConfig
from air_bot.db.mapping import Base, UserFlightDirection

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
            pool_pre_ping=True,
        )

    async def start(self) -> None:
        logger.info("DBManager: starting")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("DBManager: started")

    async def stop(self) -> None:
        logger.info("DBManager: stopping")
        await self.engine.dispose()
        logger.info("DBManager: stopped")

    async def save_or_update_flight_direction(
        self, user_id: int, direction: FlightDirection, price: int
    ) -> Optional[int]:
        try:
            async_session = async_sessionmaker(self.engine, expire_on_commit=False)
            async with async_session() as session:
                async with session.begin():
                    stmt = select(UserFlightDirection)
                    stmt = where_flight_direction_and_user(stmt, direction, user_id)
                    stmt_result = await session.scalars(stmt)
                    existing_direction = (
                        stmt_result.first()
                    )  # type: Optional[UserFlightDirection]
                    if existing_direction:
                        existing_direction.price = price
                        return existing_direction.id

                    new_direction = UserFlightDirection(
                        user_id=user_id,
                        start_code=direction.start_code,
                        start_name=direction.start_name,
                        end_code=direction.end_code,
                        end_name=direction.end_name,
                        price=price,
                        with_transfer=direction.with_transfer,
                        departure_at=direction.departure_at,
                        return_at=direction.return_at,
                    )
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
        try:
            async_session = async_sessionmaker(self.engine, expire_on_commit=False)
            async with async_session() as session:
                async with session.begin():
                    stmt = select(UserFlightDirection)
                    stmt = where_flight_direction_and_user(stmt, direction, user_id)
                    stmt_result = await session.scalars(stmt)
                    users_direction = stmt_result.one()
                    users_direction.price = price
        except Exception as e:
            logger.error(f"DatabaseError {e}")

    async def get_price(
        self, user_id: int, direction: FlightDirection
    ) -> Tuple[Optional[int], bool]:
        try:
            async_session = async_sessionmaker(self.engine, expire_on_commit=False)
            async with async_session() as session:
                async with session.begin():
                    stmt = select(UserFlightDirection.price)
                    stmt = where_flight_direction_and_user(stmt, direction, user_id)
                    stmt_result = await session.scalars(stmt)
                    return stmt_result.one(), True
        except Exception as e:
            logger.error(f"DatabaseError {e}")
            return None, False

    async def get_users_flight_directions(
        self, user_id: int
    ) -> Sequence[UserFlightDirection]:
        async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        async with async_session() as session:
            async with session.begin():
                stmt = select(UserFlightDirection).where(
                    UserFlightDirection.user_id == user_id
                )
                stmt_result = await session.scalars(stmt)
                return stmt_result.all()

    async def get_users_flight_direction(
        self, user_id: int, direction_id: int
    ) -> Optional[UserFlightDirection]:
        async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        async with async_session() as session:
            async with session.begin():
                stmt = (
                    select(UserFlightDirection)
                    .where(UserFlightDirection.user_id == user_id)
                    .where(UserFlightDirection.id == direction_id)
                )
                stmt_result = await session.scalars(stmt)
                return stmt_result.first()

    async def get_all_flight_directions(self) -> Sequence[UserFlightDirection]:
        async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        async with async_session() as session:
            async with session.begin():
                stmt = select(UserFlightDirection)
                stmt_result = await session.scalars(stmt)
                return stmt_result.all()

    async def delete_users_flight_direction(
        self, user_id: int, direction_id: int
    ) -> bool:
        """Returns True on success"""
        try:
            async_session = async_sessionmaker(self.engine, expire_on_commit=False)
            async with async_session() as session:
                async with session.begin():
                    stmt = (
                        delete(UserFlightDirection)
                        .where(UserFlightDirection.user_id == user_id)
                        .where(UserFlightDirection.id == direction_id)
                    )
                    result = await session.execute(stmt)
                    if result.rowcount == 0:  # type: ignore[attr-defined]
                        logger.warning(
                            f"Attempt to delete non existing direction for user {user_id}, direction id {direction_id}"
                        )
                    return True
        except Exception as e:
            logger.error(f"DatabaseError {e}")
            return False


def where_flight_direction_and_user(stmt, direction: FlightDirection, user_id: int):  # type: ignore[no-untyped-def]
    return (
        stmt.where(UserFlightDirection.user_id == user_id)
        .where(UserFlightDirection.start_code == direction.start_code)
        .where(UserFlightDirection.start_name == direction.start_name)
        .where(UserFlightDirection.end_code == direction.end_code)
        .where(UserFlightDirection.end_name == direction.end_name)
        .where(UserFlightDirection.with_transfer == direction.with_transfer)
        .where(UserFlightDirection.departure_at == direction.departure_at)
        .where(UserFlightDirection.return_at == direction.return_at)
    )
