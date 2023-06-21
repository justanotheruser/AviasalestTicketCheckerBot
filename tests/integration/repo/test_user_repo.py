import pytest
from sqlalchemy import select

from air_bot.adapters.repo.users import SqlAlchemyUsersRepo
from air_bot.domain.model import User


@pytest.mark.asyncio
async def test_can_add_user(mysql_session_factory):
    user_tg_id = 2**32 + 1
    async with mysql_session_factory() as session:
        users = SqlAlchemyUsersRepo(session)
        await users.add(user_tg_id)
        await session.commit()

    async with mysql_session_factory() as session:
        stmt = select(User).filter_by(user_id=user_tg_id)
        result = await session.execute(stmt)
        user = result.one()[0]
        assert user == User(user_tg_id)
