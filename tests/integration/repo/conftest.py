import datetime
import logging

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from air_bot.adapters.repo.flight_directions import SqlAlchemyFlightDirectionRepo
from air_bot.adapters.repo.orm import metadata
from air_bot.domain.model import FlightDirection


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
    yield async_sessionmaker(bind=mysql_db_engine, expire_on_commit=False)


@pytest_asyncio.fixture
def moscow2spb_one_way_direction():
    return FlightDirection(
        start_code="MOS",
        start_name="Moscow",
        end_code="LEN",
        end_name="Saint-Petersburg",
        with_transfer=False,
        departure_at="2023-05-16",
        return_at=None,
    )


@pytest_asyncio.fixture
def moscow2antalya_roundtrip_direction():
    return FlightDirection(
        start_code="MOS",
        start_name="Moscow",
        end_code="END",
        end_name="End",
        with_transfer=False,
        departure_at="2023-05-16",
        return_at="2023-06",
    )


@pytest_asyncio.fixture
async def moscow2spb_one_way_direction_id(
    mysql_session_factory, moscow2spb_one_way_direction
):
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        # last_update = datetime.datetime.now().replace(microsecond=0)
        await repo.add_direction_info(
            moscow2spb_one_way_direction, price=100, last_update=datetime.datetime.now()
        )
        await session.commit()
        return await repo.get_direction_id(moscow2spb_one_way_direction)


@pytest_asyncio.fixture
async def moscow2antalya_roundtrip_direction_id(
    mysql_session_factory, moscow2antalya_roundtrip_direction
):
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        # last_update = datetime.datetime.now().replace(microsecond=0)
        await repo.add_direction_info(
            moscow2antalya_roundtrip_direction,
            price=100,
            last_update=datetime.datetime.now(),
        )
        await session.commit()
        return await repo.get_direction_id(moscow2antalya_roundtrip_direction)


@pytest.fixture
def tomorrow_at_12am():
    result = datetime.datetime.today() + datetime.timedelta(days=1)
    return result.replace(hour=12, minute=0, second=0, microsecond=0)


@pytest.fixture
def tomorrow_at_6_30pm():
    result = datetime.datetime.today() + datetime.timedelta(days=1)
    return result.replace(hour=18, minute=30, second=0, microsecond=0)


@pytest.fixture
def next_week():
    result = datetime.datetime.today() + datetime.timedelta(days=7)
    return result.replace(hour=12, minute=0, second=0, microsecond=0)


@pytest.fixture
def two_hours():
    return datetime.timedelta(hours=2)
