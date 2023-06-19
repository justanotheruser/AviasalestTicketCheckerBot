import pytest

from air_bot.adapters.tickets_api import AviasalesTicketsApi
from air_bot.domain.model import FlightDirection
from air_bot.domain.exceptions import TicketsAPIError

def moscow_spb_direction(with_transfer: bool, departure_at: str, return_at: str | None):
    return FlightDirection(
        start_code="MOW",
        start_name="Москва",
        end_code="LED",
        end_name="Санкт-Петербург",
        with_transfer=with_transfer,
        departure_at=departure_at,
        return_at=return_at,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("with_transfer", [False, True])
@pytest.mark.parametrize("with_return", [False, True])
async def test_get_tickets_success(
    http_session, token, this_month, next_month, with_transfer, with_return
):
    api = AviasalesTicketsApi(http_session, token, "rub")
    return_at = next_month if with_return else None
    direction = moscow_spb_direction(
        with_transfer=with_transfer, departure_at=this_month, return_at=return_at
    )
    tickets = await api.get_tickets(direction, limit=2)
    assert len(tickets) == 2
    if with_return:
        for ticket in tickets:
            assert ticket.return_at and ticket.duration_back


@pytest.mark.asyncio
async def test_diff_between_max_depart_date_and_min_return_date_exceeds_supported_minimum(
    http_session, token, this_month, next_next_month, caplog
):
    api = AviasalesTicketsApi(http_session, token, "rub")
    direction = moscow_spb_direction(
        with_transfer=True, departure_at=this_month, return_at=next_next_month
    )
    with pytest.raises(TicketsAPIError):
        await api.get_tickets(direction)
    assert len(caplog.messages) == 1
    assert (
        "diff between max depart date and min return date exceeds supported maximum of 30"
        in caplog.messages[0]
    )
