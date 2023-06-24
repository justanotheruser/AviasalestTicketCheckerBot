from dataclasses import dataclass

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from air_bot.adapters.repo import orm
from air_bot.domain import model
from air_bot.domain.repository import AbstractUserDirectionRepo


@dataclass(kw_only=True)
class UserDirectionDB:
    user_id: int
    direction_id: int


class SqlAlchemyUserDirectionRepo(AbstractUserDirectionRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def add(self, user_id: int, direction_id: int):
        stmt = text(
            "INSERT INTO users_directions (user_id, direction_id) VALUES (:user_id, :direction_id)"
        )
        stmt = stmt.bindparams(user_id=user_id, direction_id=direction_id)
        await self.session.execute(stmt)

    async def get_user_directions(self, user_id: int) -> list[int]:
        stmt = select(UserDirectionDB).where(
            orm.users_directions_table.c.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return [row[0].direction_id for row in result.all()]
