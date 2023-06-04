import datetime

import pytest
import pytest_asyncio
from data_for_tests import FLIGHT_DIRECTION_NO_RETURN, FLIGHT_DIRECTION_WITH_RETURN

from air_bot.adapters.repository import (
    SqlAlchemyFlightDirectionRepo,
    SqlAlchemyUserDirectionRepo,
)


@pytest.mark.asyncio
async def test_add_direction_and_get_direction_id(mysql_session_factory):
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        for direction in [FLIGHT_DIRECTION_NO_RETURN, FLIGHT_DIRECTION_WITH_RETURN]:
            last_update = datetime.datetime.now().replace(microsecond=0)
            await repo.add_direction_info(direction, price=100, last_update=last_update)
        await session.commit()

    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        first_direction_id = await repo.get_direction_id(FLIGHT_DIRECTION_NO_RETURN)
        second_direction_id = await repo.get_direction_id(FLIGHT_DIRECTION_WITH_RETURN)
        assert first_direction_id
        assert second_direction_id
        assert first_direction_id != second_direction_id
