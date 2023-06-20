from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


class AbstractUserRepo(ABC):
    @abstractmethod
    async def add(self, user_id: int):
        raise NotImplementedError


class SqlAlchemyUsersRepo(AbstractUserRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def add(self, user_id: int):
        stmt = text(
            "INSERT INTO user (user_id) VALUES (:user_id)"
        )
        stmt = stmt.bindparams(user_id=user_id)
        await self.session.execute(stmt)
