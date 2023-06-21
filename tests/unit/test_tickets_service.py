import pytest
from fakes import (
    FakeFlightDirectionRepo,
    FakeTicketRepo,
    FakeTicketsApi,
    FakeUserFlightDirectionRepo,
)

from air_bot.domain.model import FlightDirection
from air_bot.service.tickets_service import TicketsService

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
async def test_add_new_direction(direction):
    fake_flight_direction_repo = FakeFlightDirectionRepo()
    fake_user_flight_direction_repo = FakeUserFlightDirectionRepo()
    fake_ticket_repo = FakeTicketRepo()
    fake_tickets_api = FakeTicketsApi()
    tickets_service = TicketsService(
        fake_flight_direction_repo,
        fake_user_flight_direction_repo,
        fake_ticket_repo,
        fake_tickets_api,
    )
    user_id = 1
    tickets = await tickets_service.track(user_id, direction)
    # assert tickets == # TODO: FakeTicketsAPI
