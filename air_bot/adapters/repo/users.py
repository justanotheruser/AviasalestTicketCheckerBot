from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from air_bot.domain.model import User
from air_bot.domain.repository import AbstractUserRepo


class DuplicatedUserIdError(Exception):
    pass


class SqlAlchemyUsersRepo(AbstractUserRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def add(self, user_id: int):
        stmt = text("INSERT INTO users (user_id) VALUES (:user_id)")
        stmt = stmt.bindparams(user_id=user_id)
        await self.session.execute(stmt)

    async def exists(self, user_id: int) -> bool:
        stmt = select(User).filter_by(user_id=user_id)
        result = await self.session.execute(stmt)
        row = result.first()
        return row is not None
