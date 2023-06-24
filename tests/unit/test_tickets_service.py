import datetime
import random

import pytest
from fakes import FakeTicketsApi, FakeUnitOfWork

from air_bot.domain.model import FlightDirection, Ticket
from air_bot.service import track

"""
def random_flight_direction(with_return: bool = False) -> FlightDirection:
    letters = string.ascii_uppercase
    start_code = "".join(random.choice(letters) for i in range(3))
    end_code = "".join(random.choice(letters) for i in range(3))
    with_transfer = random.choice([True, False])
    departure_at = "2023-06-04"
    return_at = "2023-06-05" if with_return else None
    return FlightDirection(
        start_code=start_code,
        start_name=start_code,
        end_code=end_code,
        end_name=end_code,
        with_transfer=with_transfer,
        departure_at=departure_at,
        return_at=return_at,
    )
"""

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
    tickets_api = FakeTicketsApi()
    uow = FakeUnitOfWork()
    user_id = 1
    tickets = await track(user_id, direction, tickets_api, uow)
    assert tickets == []

    async with uow:
        direction_id = await uow.flight_directions.get_direction_id(direction)
        directions_info = await uow.flight_directions.get_directions_info(
            [direction_id]
        )
        user_directions = await uow.users_directions.get_directions(user_id)
    assert directions_info[0].direction == direction
    assert user_directions == [direction_id]


def get_random_ticket(roundtrip: bool):
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
    return Ticket(
        price=random.randint(100, 100000) + 0.5,
        departure_at=departure_at,
        duration_to=duration_to,
        return_at=return_at,
        duration_back=duration_back,
        link=link,
    )


from unittest.mock import AsyncMock, Mock


@pytest.mark.asyncio
async def test_add_new_direction_and_get_tickets():
    direction = FlightDirection(
        start_code="MOS",
        start_name="Moscow",
        end_code="END",
        end_name="End",
        with_transfer=False,
        departure_at="2023-05-16",
        return_at="2023-06",
    )
    tickets = [get_random_ticket(roundtrip=True), get_random_ticket(roundtrip=True)]
    tickets_api = Mock(get_tickets=AsyncMock(return_value=tickets))
    uow = FakeUnitOfWork()
    user_id = 1
    received_tickets = await track(user_id, direction, tickets_api, uow)
    assert received_tickets == tickets
