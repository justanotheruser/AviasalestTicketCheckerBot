import pytest
from sqlalchemy.exc import IntegrityError

from air_bot.adapters.repo.users_directions import SqlAlchemyUserDirectionRepo


@pytest.mark.asyncio
async def test_cant_add_same_direction_for_user_twice(
    mysql_session_factory, moscow2spb_one_way_direction_id
):
    async with mysql_session_factory() as session:
        repo = SqlAlchemyUserDirectionRepo(session)
        await repo.add(1, moscow2spb_one_way_direction_id)
        with pytest.raises(IntegrityError):
            await repo.add(1, moscow2spb_one_way_direction_id)


# @pytest.mark.asyncio
# async def test_delete_from_users_directions_when_direction_deleted(mysql_session_factory, direction_id):
