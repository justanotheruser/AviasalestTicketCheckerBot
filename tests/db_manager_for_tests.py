from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import delete
from air_bot.db.mapping import UserFlightDirection

from air_bot.db.db_manager import DBManager


class DBManagerForTests(DBManager):
    async def delete_all(self):
        async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        async with async_session() as session:
            async with session.begin():
                stmt = delete(UserFlightDirection)
                await session.execute(stmt)
