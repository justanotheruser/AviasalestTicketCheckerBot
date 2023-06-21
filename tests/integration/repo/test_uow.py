import datetime
from typing import Optional

import pytest
from data_for_tests import FLIGHT_DIRECTION_NO_RETURN, FLIGHT_DIRECTION_WITH_RETURN
from sqlalchemy import text

from air_bot.domain.model import FlightDirection
from air_bot.adapters.repo.uow import SqlAlchemyUnitOfWork


@pytest.mark.asyncio
async def insert_flight_direction(
    session,
    direction: FlightDirection,
    price: Optional[float],
    last_update: datetime.datetime,
):
    query = text(
        "INSERT INTO flight_direction (start_code, start_name, end_code, end_name, "
        "with_transfer, departure_at, return_at, price, last_update) VALUES (:start_code, :start_name,"
        ":end_code, :end_name, :with_transfer, :departure_at, :return_at, :price, :last_update)"
    ).bindparams(
        start_code=direction.start_code,
        start_name=direction.start_name,
        end_code=direction.end_code,
        end_name=direction.end_name,
        with_transfer=direction.with_transfer,
        departure_at=direction.departure_at,
        return_at=direction.return_at,
        price=price,
        last_update=last_update,
    )
    await session.execute(query)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "direction", [FLIGHT_DIRECTION_NO_RETURN, FLIGHT_DIRECTION_WITH_RETURN]
)
async def test_uow_can_retrieve_flight_direction_info(mysql_session_factory, direction):
    last_update = datetime.datetime.now().replace(microsecond=0)

    async with mysql_session_factory() as session:
        await insert_flight_direction(session, direction, 220.5, last_update)
        await session.commit()

    uow = SqlAlchemyUnitOfWork(mysql_session_factory)
    async with uow:
        direction_info = await uow.flight_direction.get_direction_info(direction)
        assert direction_info.direction == direction
        assert direction_info.price == 220.5
        assert direction_info.last_update == last_update
