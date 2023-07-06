import pytest
from pytest_unordered import unordered
from sqlalchemy.exc import IntegrityError

from air_bot.adapters.repo.flight_directions import SqlAlchemyFlightDirectionRepo
from air_bot.adapters.repo.users_directions import SqlAlchemyUserDirectionRepo


@pytest.mark.asyncio
async def test_add_direction_for_user_and_get_them_back(
    mysql_session_factory,
    moscow2spb_one_way_direction_id,
    moscow2antalya_roundtrip_direction_id,
):
    user_id = 1
    async with mysql_session_factory() as session:
        repo = SqlAlchemyUserDirectionRepo(session)
        await repo.add(user_id, moscow2spb_one_way_direction_id)
        await repo.add(user_id, moscow2antalya_roundtrip_direction_id)
        await session.commit()

    async with mysql_session_factory() as session:
        repo = SqlAlchemyUserDirectionRepo(session)
        user_direction_ids = await repo.get_directions(user_id)
    assert user_direction_ids == unordered(
        [moscow2spb_one_way_direction_id, moscow2antalya_roundtrip_direction_id]
    )


@pytest.mark.asyncio
async def test_get_directions_only_for_specified_user(
    mysql_session_factory,
    moscow2spb_one_way_direction_id,
    moscow2antalya_roundtrip_direction_id,
):
    async with mysql_session_factory() as session:
        repo = SqlAlchemyUserDirectionRepo(session)
        await repo.add(1, moscow2spb_one_way_direction_id)
        await repo.add(2, moscow2antalya_roundtrip_direction_id)
        await session.commit()
    async with mysql_session_factory() as session:
        repo = SqlAlchemyUserDirectionRepo(session)
        user_direction_ids = await repo.get_directions(1)
    assert user_direction_ids == [moscow2spb_one_way_direction_id]


@pytest.mark.asyncio
async def test_cant_add_same_direction_for_user_twice(
    mysql_session_factory, moscow2spb_one_way_direction_id
):
    async with mysql_session_factory() as session:
        repo = SqlAlchemyUserDirectionRepo(session)
        await repo.add(1, moscow2spb_one_way_direction_id)
        with pytest.raises(IntegrityError):
            await repo.add(1, moscow2spb_one_way_direction_id)


@pytest.mark.asyncio
async def test_remove_from_users_directions(
    mysql_session_factory, moscow2spb_one_way_direction_id
):
    user_id = 1
    async with mysql_session_factory() as session:
        repo = SqlAlchemyUserDirectionRepo(session)
        await repo.add(user_id, moscow2spb_one_way_direction_id)
        await session.commit()

    async with mysql_session_factory() as session:
        repo = SqlAlchemyUserDirectionRepo(session)
        await repo.remove(user_id, moscow2spb_one_way_direction_id)
        await session.commit()

    async with mysql_session_factory() as session:
        repo = SqlAlchemyUserDirectionRepo(session)
        user_directions = await repo.get_directions(user_id)
    assert user_directions == []


@pytest.mark.asyncio
async def test_delete_from_users_directions_when_direction_deleted(
    mysql_session_factory, moscow2spb_one_way_direction_id
):
    user_id = 1
    async with mysql_session_factory() as session:
        repo = SqlAlchemyUserDirectionRepo(session)
        await repo.add(user_id, moscow2spb_one_way_direction_id)
        await session.commit()

    async with mysql_session_factory() as session:
        repo = SqlAlchemyFlightDirectionRepo(session)
        await repo.delete_direction(moscow2spb_one_way_direction_id)
        await session.commit()

    async with mysql_session_factory() as session:
        repo = SqlAlchemyUserDirectionRepo(session)
        user_directions = await repo.get_directions(user_id)
    assert user_directions == []
