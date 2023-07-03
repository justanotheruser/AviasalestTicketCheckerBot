import datetime
import random
from unittest.mock import AsyncMock, Mock

import pytest
from fakes import FakeUnitOfWork
from pytest_unordered import unordered

from air_bot.domain.model import FlightDirection, Ticket
from air_bot.service.user import track

FLIGHT_DIRECTION_NO_RETURN = FlightDirection(
    start_code="STA",
    start_name="Start",
    end_code="END",
    end_name="End",
    with_transfer=False,
    departure_at="2023-05-16",
    return_at=None,
)

FLIGHT_DIRECTION_WITH_RETURN = FlightDirection(
    start_code="STA",
    start_name="Start",
    end_code="END",
    end_name="End",
    with_transfer=False,
    departure_at="2023-05-16",
    return_at="2023-06",
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "direction", [FLIGHT_DIRECTION_NO_RETURN, FLIGHT_DIRECTION_WITH_RETURN]
)
async def test_add_new_direction_with_no_tickets_available(direction):
    tickets_api = Mock(get_tickets=AsyncMock(return_value=[]))
    uow = FakeUnitOfWork()
    user_id = 1
    tickets = await track(user_id, direction, tickets_api, uow)
    assert tickets == []
    direction_id = await uow.flight_directions.get_direction_id(direction)
    directions_info = await uow.flight_directions.get_directions_info([direction_id])
    user_directions = await uow.users_directions.get_directions(user_id)
    assert directions_info[0].direction == direction
    assert user_directions == [direction_id]


def get_random_tickets(roundtrip: bool, amount: int):
    tickets = []
    for _ in range(amount):
        departure_at = datetime.datetime.today().replace(microsecond=0)
        duration_to = datetime.timedelta(minutes=random.randint(60, 360))
        link = "some link"
        link = "".join(random.sample(link, len(link)))
        if roundtrip:
            return_at = datetime.datetime.today() + datetime.timedelta(days=1)
            return_at = return_at.replace(microsecond=0)
            duration_back = datetime.timedelta(minutes=random.randint(60, 360))
        else:
            return_at = None
            duration_back = None
        tickets.append(
            Ticket(
                price=random.randint(100, 100000) + 0.5,
                departure_at=departure_at,
                duration_to=duration_to,
                return_at=return_at,
                duration_back=duration_back,
                link=link,
            )
        )
    return tickets


@pytest.mark.asyncio
async def test_add_new_direction_and_get_tickets():
    tickets = get_random_tickets(roundtrip=True, amount=2)
    tickets_api = Mock(get_tickets=AsyncMock(return_value=tickets))
    uow = FakeUnitOfWork()
    user_id = 1
    received_tickets = await track(
        user_id, FLIGHT_DIRECTION_WITH_RETURN, tickets_api, uow
    )
    assert received_tickets == tickets
    direction_id = await uow.flight_directions.get_direction_id(
        FLIGHT_DIRECTION_WITH_RETURN
    )
    directions_info = await uow.flight_directions.get_directions_info([direction_id])
    user_directions = await uow.users_directions.get_directions(user_id)
    assert directions_info[0].direction == FLIGHT_DIRECTION_WITH_RETURN
    assert user_directions == [direction_id]
    tickets_in_db = await uow.tickets.get_direction_tickets(direction_id)
    assert tickets_in_db == unordered(tickets)


@pytest.mark.asyncio
async def test_get_tickets_from_repo_for_existing_direction():
    tickets = get_random_tickets(roundtrip=False, amount=3)
    tickets_api = Mock()
    uow = FakeUnitOfWork()
    direction_id = await uow.flight_directions.add_direction_info(
        FLIGHT_DIRECTION_NO_RETURN, 1000, datetime.datetime.now()
    )
    await uow.tickets.add(tickets, direction_id)
    user_id = 1
    received_tickets = await track(
        user_id, FLIGHT_DIRECTION_NO_RETURN, tickets_api, uow
    )
    assert received_tickets == tickets


@pytest.mark.asyncio
async def test_get_tickets_from_api_for_existing_direction_with_no_tickets():
    tickets = get_random_tickets(roundtrip=True, amount=2)
    tickets_api = Mock(get_tickets=AsyncMock(return_value=tickets))
    uow = FakeUnitOfWork()
    user_id = 1
    direction_id = await uow.flight_directions.add_direction_info(
        FLIGHT_DIRECTION_WITH_RETURN, 1000, datetime.datetime.now()
    )
    received_tickets = await track(
        user_id, FLIGHT_DIRECTION_WITH_RETURN, tickets_api, uow
    )
    assert received_tickets == tickets
    tickets_in_repo = await uow.tickets.get_direction_tickets(direction_id)
    assert tickets_in_repo == tickets
