import datetime

import pytest

from air_bot.adapters.repo.flight_directions import SqlAlchemyFlightDirectionRepo


@pytest.mark.asyncio
async def test_add_direction_and_get_direction_id(
    mysql_session_factory,
    moscow2spb_one_way_direction,
    moscow2antalya_roundtrip_direction,
):
    inserted_direction_ids = []
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        for direction in [
            moscow2spb_one_way_direction,
            moscow2antalya_roundtrip_direction,
        ]:
            last_update = datetime.datetime.now().replace(microsecond=0)
            direction_id = await repo.add_direction_info(direction, price=100, last_update=last_update)
            inserted_direction_ids.append(direction_id)
        await session.commit()

    selected_direction_ids = []
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        for direction in [
            moscow2spb_one_way_direction,
            moscow2antalya_roundtrip_direction,
        ]:
            direction_id = await repo.get_direction_id(direction)
            selected_direction_ids.append(direction_id)

    assert inserted_direction_ids == selected_direction_ids
