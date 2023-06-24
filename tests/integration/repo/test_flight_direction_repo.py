import datetime

import pytest

from air_bot.adapters.repo.flight_directions import SqlAlchemyFlightDirectionRepo


@pytest.mark.asyncio
async def test_add_direction_and_get_direction_id(
    mysql_session_factory,
    moscow2spb_one_way_direction,
    moscow2antalya_roundtrip_direction,
):
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        for direction in [
            moscow2spb_one_way_direction,
            moscow2antalya_roundtrip_direction,
        ]:
            last_update = datetime.datetime.now().replace(microsecond=0)
            await repo.add_direction_info(direction, price=100, last_update=last_update)
        await session.commit()

    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        first_direction_id = await repo.get_direction_id(moscow2spb_one_way_direction)
        second_direction_id = await repo.get_direction_id(
            moscow2antalya_roundtrip_direction
        )
        assert first_direction_id
        assert second_direction_id
        assert first_direction_id != second_direction_id
