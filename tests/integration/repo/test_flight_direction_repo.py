from dataclasses import asdict
from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from air_bot.adapters.repo.flight_directions import SqlAlchemyFlightDirectionRepo
from air_bot.domain.model import FlightDirection


@pytest.mark.asyncio
async def test_add_direction_and_get_direction_id(
    mysql_session_factory: async_sessionmaker,
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
            last_update = datetime.now().replace(microsecond=0)
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
            direction_id = await repo.get_direction_id(direction)  # type: ignore[assignment]
            selected_direction_ids.append(direction_id)

    assert inserted_direction_ids == selected_direction_ids


@pytest.mark.asyncio
async def test_get_directions_by_ids(
    mysql_session_factory: async_sessionmaker,
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
            last_update = datetime.now().replace(microsecond=0)
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
async def test_get_non_existing_directions_by_ids(
    mysql_session_factory: async_sessionmaker,
):
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        directions = await repo.get_directions_info([-1])
        assert directions == []


@pytest.mark.asyncio
async def test_get_non_existing_direction_by_id(
    mysql_session_factory: async_sessionmaker,
):
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        direction = await repo.get_direction_info(-1)
        assert direction is None


@pytest.mark.asyncio
async def test_get_most_outdated_directions(
    mysql_session_factory: async_sessionmaker, moscow2spb_one_way_direction
):
    direction = moscow2spb_one_way_direction
    earliest_direction_last_update = datetime.now()
    time_step = 5
    last_updates = [
        earliest_direction_last_update + timedelta(minutes=m)
        for m in range(0, 30, time_step)
    ]
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        for last_update in last_updates:
            await repo.add_direction_info(direction, 100, last_update)
        await session.commit()

    # Time stamp between 1 and 2 place
    last_update = last_updates[-1] - timedelta(minutes=time_step // 2)
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        directions = await repo.get_directions_with_last_update_try_before(
            last_update, limit=100
        )
    assert len(directions) == len(last_updates) - 1
    selected_update_times = [d.last_update for d in directions]
    assert selected_update_times == sorted(selected_update_times)
    assert all(selected_lu < last_update for selected_lu in selected_update_times)

    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        directions = await repo.get_directions_with_last_update_try_before(
            last_update, limit=1
        )
    assert len(directions) == 1

    last_update = earliest_direction_last_update - timedelta(seconds=1)
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        directions = await repo.get_directions_with_last_update_try_before(
            last_update, limit=100
        )
    assert directions == []


@pytest.mark.asyncio
@pytest.mark.parametrize("new_price", [200.5, None])
async def test_update_price(
    mysql_session_factory: async_sessionmaker,
    moscow2spb_one_way_direction,
    new_price: float | None,
):
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        direction_id = await repo.add_direction_info(
            moscow2spb_one_way_direction, 100, datetime.now()
        )
        await session.commit()

    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        last_update = datetime.now().replace(microsecond=0)
        await repo.update_price(direction_id, new_price, last_update)
        await session.commit()

    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        directions = await repo.get_directions_info([direction_id])
        direction = directions[0]
        await session.commit()
    assert direction.price == new_price
    assert direction.last_update == last_update


@pytest.mark.asyncio
async def test_delete_direction(
    mysql_session_factory: async_sessionmaker, moscow2antalya_roundtrip_direction
):
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        direction_id = await repo.add_direction_info(
            moscow2antalya_roundtrip_direction, 100, datetime.now()
        )
        await session.commit()

    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        await repo.delete_direction(direction_id)
        await session.commit()

    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        assert await repo.get_direction_info(direction_id) is None


@pytest.mark.asyncio
async def test_delete_outdated_directions(
    mysql_session_factory: async_sessionmaker, moscow2antalya_roundtrip_direction
):
    direction_dict = asdict(moscow2antalya_roundtrip_direction)
    day_before_yesterday = datetime.now() - timedelta(days=2)
    direction_dict["departure_at"] = datetime.strftime(day_before_yesterday, "%Y-%m-%d")
    direction = FlightDirection(**direction_dict)
    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        await repo.add_direction_info(direction, 100, datetime.now())
        await session.commit()

    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        await repo.delete_outdated_directions()
        await session.commit()

    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        assert await repo.get_direction_id(direction) is None
