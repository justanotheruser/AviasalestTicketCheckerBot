import logging
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from air_bot.config import config


class AbstractSessionMaker(ABC):
    @abstractmethod
    def __call__(self):
        raise NotImplementedError


class SessionMaker(AbstractSessionMaker):
    def __init__(self):
        logging.basicConfig()
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
        self.engine = create_async_engine(config.get_mysql_uri(),
                                          pool_pre_ping=True)

    async def start(self):
        self.session_maker = async_sessionmaker(
            bind=self.engine, expire_on_commit=False
        )

    def __call__(self):
        return self.session_maker()

    async def stop(self):
        await self.engine.dispose()
