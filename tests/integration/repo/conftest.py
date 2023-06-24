import datetime
import logging

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from air_bot.adapters.repo.flight_directions import SqlAlchemyFlightDirectionRepo
from air_bot.adapters.repo.orm import metadata
from data_for_tests import FLIGHT_DIRECTION_NO_RETURN


@pytest_asyncio.fixture
async def mysql_db_engine():
    load_dotenv()
    from air_bot.config import config

    engine = create_async_engine(config.get_mysql_uri())

    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    async def delete_all():
        async_session = async_sessionmaker(engine)
        async with async_session() as session:
            async with session.begin():
                await session.execute(text("DELETE FROM historic_flight_directions"))
                await session.execute(text("DELETE FROM tickets"))
                await session.execute(text("DELETE FROM flight_directions"))
                await session.execute(text("DELETE FROM users"))
                await session.execute(text("DELETE FROM users_directions"))

    await delete_all()
    yield engine
    await delete_all()


@pytest_asyncio.fixture
async def mysql_session_factory(mysql_db_engine):
    yield async_sessionmaker(bind=mysql_db_engine)


@pytest_asyncio.fixture
async def direction_id(mysql_session_factory):
    direction = FLIGHT_DIRECTION_NO_RETURN
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        last_update = datetime.datetime.now().replace(microsecond=0)
        await repo.add_direction_info(direction, price=100, last_update=last_update)
        await session.commit()
        return await repo.get_direction_id(direction)


@pytest.fixture
def today():
    return datetime.datetime.now()


@pytest.fixture
def two_hours():
    return datetime.timedelta(hours=2)
