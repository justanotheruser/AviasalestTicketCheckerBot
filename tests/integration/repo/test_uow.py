import datetime

import pytest

from air_bot.adapters.repo.uow import SqlAlchemyUnitOfWork


@pytest.mark.asyncio
async def test_uow_commit(mysql_session_factory, moscow2spb_one_way_direction):
    last_update = datetime.datetime.now().replace(microsecond=0)

    uow = SqlAlchemyUnitOfWork(mysql_session_factory)
    async with uow:
        await uow.flight_directions.add_direction_info(
            moscow2spb_one_way_direction, 220.5, last_update
        )
        await uow.commit()

    uow = SqlAlchemyUnitOfWork(mysql_session_factory)
    async with uow:
        direction_info = await uow.flight_directions.get_direction_info(
            moscow2spb_one_way_direction
        )
        await uow.commit()
    assert direction_info.direction == moscow2spb_one_way_direction
    assert direction_info.price == 220.5
    assert direction_info.last_update == last_update


@pytest.mark.asyncio
async def test_uow_rollback(mysql_session_factory, moscow2spb_one_way_direction):
    last_update = datetime.datetime.now().replace(microsecond=0)

    uow = SqlAlchemyUnitOfWork(mysql_session_factory)
    async with uow:
        await uow.flight_directions.add_direction_info(
            moscow2spb_one_way_direction, 220.5, last_update
        )

    uow = SqlAlchemyUnitOfWork(mysql_session_factory)
    async with uow:
        direction_info = await uow.flight_directions.get_direction_info(
            moscow2spb_one_way_direction
        )
        await uow.commit()
    assert direction_info is None
