import pytest
from pytest_unordered import unordered

from air_bot.adapters.repo.tickets import SqlAlchemyTicketRepo
from air_bot.domain.model import Ticket


@pytest.mark.asyncio
async def test_add_tickets_for_direction_and_get_them_back(
    mysql_session_factory,
    moscow2spb_one_way_direction_id,
    moscow2antalya_roundtrip_direction_id,
    tomorrow_at_12am,
    tomorrow_at_6_30pm,
    next_week,
    two_hours,
):
    moscow2spb_tickets = [
        Ticket(
            price=100, departure_at=tomorrow_at_12am, duration_to=two_hours, link="link"
        ),
        Ticket(
            price=200,
            departure_at=tomorrow_at_6_30pm,
            duration_to=two_hours,
            link="link",
        ),
    ]
    moscow2antalya_tickets = [
        Ticket(
            price=100,
            departure_at=tomorrow_at_12am,
            duration_to=two_hours,
            link="link",
            return_at=next_week,
            duration_back=two_hours,
        )
    ]
    async with mysql_session_factory() as session:
        repo = SqlAlchemyTicketRepo(session)
        await repo.add(moscow2spb_tickets, moscow2spb_one_way_direction_id)
        await repo.add(moscow2antalya_tickets, moscow2antalya_roundtrip_direction_id)
        await session.commit()

    async with mysql_session_factory() as session:
        repo = SqlAlchemyTicketRepo(session)
        selected_tickets = await repo.get_direction_tickets(
            moscow2spb_one_way_direction_id
        )
        await session.commit()
    assert moscow2spb_tickets == unordered(selected_tickets)

    async with mysql_session_factory() as session:
        repo = SqlAlchemyTicketRepo(session)
        selected_tickets = await repo.get_direction_tickets(
            moscow2spb_one_way_direction_id, limit=1
        )
        await session.commit()
    assert selected_tickets == [moscow2spb_tickets[0]]
