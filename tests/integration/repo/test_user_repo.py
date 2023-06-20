import pytest
from sqlalchemy import select

from air_bot.adapters.repo.users_repo import SqlAlchemyUsersRepo
from air_bot.domain.model import User


@pytest.mark.asyncio
async def test_can_add_user(mysql_session_factory):
    async with mysql_session_factory() as session:
        users = SqlAlchemyUsersRepo(session)
        await users.add(42)
        await session.commit()

    async with mysql_session_factory() as session:
        stmt = select(User).filter_by(user_id=42)
        result = await session.execute(stmt)
        user = result.one()
        assert user == User(42)
