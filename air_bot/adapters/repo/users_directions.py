from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.repo import orm
from air_bot.domain import model
from air_bot.domain.repository import AbstractUserDirectionRepo


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

    # TODO: figure out why we need it
    async def get_users_direction(self, user_id: int, direction_id: int):
        stmt = select(model.UserDirection).where(
            orm.users_directions_table.c.user_id == user_id
        )
        stmt = stmt.where(orm.users_directions_table.c.direction_id == direction_id)
        await self.session.execute(stmt)
