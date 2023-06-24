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
            direction_id = await repo.add_direction_info(
                direction, price=100, last_update=last_update
            )
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


@pytest.mark.asyncio
async def test_get_directions_by_ids(
    mysql_session_factory,
    moscow2spb_one_way_direction,
    moscow2antalya_roundtrip_direction,
):
    directions = [
        moscow2spb_one_way_direction,
        moscow2antalya_roundtrip_direction,
    ]
    inserted_direction_ids = []
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        for direction in directions:
            last_update = datetime.datetime.now().replace(microsecond=0)
            direction_id = await repo.add_direction_info(
                direction, price=100, last_update=last_update
            )
            inserted_direction_ids.append(direction_id)
        await session.commit()

    # We can get individual directions
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        for i in range(len(directions)):
            direction_infos = await repo.get_directions_info(
                [inserted_direction_ids[i]]
            )
            assert len(direction_infos) == 1
            assert direction_infos[0].direction == directions[i]

    # And we can get list of directions
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        direction_infos = await repo.get_directions_info(inserted_direction_ids)
        assert len(direction_infos) == len(inserted_direction_ids)


@pytest.mark.asyncio
async def test_get_non_existing_direction_by_ids(mysql_session_factory):
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        directions = await repo.get_directions_info([-1])
        assert directions == []


@pytest.mark.asyncio
async def test_update_price(mysql_session_factory, moscow2spb_one_way_direction):
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        direction_id = await repo.add_direction_info(
            moscow2spb_one_way_direction, 100, datetime.datetime.now())
        await session.commit()

    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        last_update = datetime.datetime.now().replace(microsecond=0)
        await repo.update_price(direction_id, 200, last_update)
        await session.commit()

    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        directions = await repo.get_directions_info([direction_id])
        direction = directions[0]
        await session.commit()
    assert direction.price == 200
    assert direction.last_update == last_update
