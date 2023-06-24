import pytest
from sqlalchemy.exc import IntegrityError

from pytest_unordered import unordered
from air_bot.adapters.repo.tickets import SqlAlchemyTicketRepo
from air_bot.domain.model import Ticket


@pytest.mark.asyncio
async def test_cant_add_same_direction_for_user_twice(
        mysql_session_factory, direction_id, today, two_hours
):
    inserted_tickets = [
        Ticket(price=100, departure_at=today, duration_to=two_hours, link="ticket link")]
    async with mysql_session_factory() as session:
        repo = SqlAlchemyTicketRepo(session)
        await repo.add(inserted_tickets, direction_id)
        await session.commit()

    async with mysql_session_factory() as session:
        repo = SqlAlchemyTicketRepo(session)
        selected_tickets = await repo.get_direction_tickets(direction_id)

    assert inserted_tickets == unordered(selected_tickets)
