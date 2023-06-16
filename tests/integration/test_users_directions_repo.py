import datetime

import pytest
import pytest_asyncio
from data_for_tests import FLIGHT_DIRECTION_NO_RETURN
from sqlalchemy.exc import IntegrityError

from air_bot.adapters.repository import (
    SqlAlchemyFlightDirectionRepo,
    SqlAlchemyUserDirectionRepo,
)


@pytest_asyncio.fixture
async def direction_id(mysql_session_factory):
    direction = FLIGHT_DIRECTION_NO_RETURN
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        last_update = datetime.datetime.now().replace(microsecond=0)
        await repo.add_direction_info(direction, price=100, last_update=last_update)
        await session.commit()
        return await repo.get_direction_id(direction)


@pytest.mark.asyncio
async def test_cant_add_same_direction_for_user_twice(
    mysql_session_factory, direction_id
):
    async with mysql_session_factory() as session:
        repo = SqlAlchemyUserDirectionRepo(session)
        await repo.add(1, direction_id)
        with pytest.raises(IntegrityError):
            await repo.add(1, direction_id)


# @pytest.mark.asyncio
# async def test_delete_from_users_directions_when_direction_deleted(mysql_session_factory, direction_id):
