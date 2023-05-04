from air_bot.handlers.add_flight_direction import show_tickets

import pytest


@pytest.mark.skip
@pytest.mark.asyncio
async def test_simple(mocker):
    message = mocker.Mock()
    user_id = 123456789
    aiohttp_session = mocker.Mock()
    state = mocker.Mock()
    db = mocker.Mock()
    ticket_price_checker = mocker.Mock()
    await show_tickets(
        message, user_id, aiohttp_session, state, db, ticket_price_checker
    )
