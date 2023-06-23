import logging

import pytest_asyncio
from air_bot.adapters.repo.orm import metadata
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


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
                await session.execute(text("DELETE FROM flight_direction"))
                await session.execute(text("DELETE FROM user"))
                await session.execute(text("DELETE FROM users_directions"))

    await delete_all()
    yield engine
    await delete_all()


@pytest_asyncio.fixture
async def mysql_session_factory(mysql_db_engine):
    yield async_sessionmaker(bind=mysql_db_engine)
