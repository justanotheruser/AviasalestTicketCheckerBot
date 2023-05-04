from unittest.mock import AsyncMock, Mock, patch

import pytest

from air_bot.bot_types import FlightDirection
from air_bot.checker.ticket_price_checker import TicketPriceChecker


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


@pytest.mark.parametrize(
    "direction", [FLIGHT_DIRECTION_NO_RETURN, FLIGHT_DIRECTION_WITH_RETURN]
)
@pytest.mark.ticket_price_checker_config_values(
    {
        "check_interval": 30,
        "check_interval_units": "seconds",
        "price_reduction_threshold_percents": 10,
    }
)
async def test_schedule_check_receive_no_tickets(
    ticket_price_checker_config, db, mocker, direction
):
    bot = mocker.Mock()
    bot.send_message = AsyncMock()
    aviasales_api = mocker.Mock()
    aviasales_api.get_cheapest_ticket = AsyncMock()
    scheduler = mocker.MagicMock()
    schedule_every_seconds = mocker.MagicMock()
    scheduler.schedule_every_seconds = schedule_every_seconds
    checker = TicketPriceChecker(
        bot, aviasales_api, db, scheduler, ticket_price_checker_config
    )
    assert aviasales_api.mock_calls == []

    user_id = 1
    checker.schedule_check(user_id, direction)
    assert schedule_every_seconds.call_count == 2
    first_call_args = schedule_every_seconds.call_args_list[0][0]
    assert first_call_args[0] == 5  # Check that 'reload_config' is scheduler
    second_call_args = schedule_every_seconds.call_args_list[1][0]
    seconds, scheduled_fn, scheduled_fn_args = (
        second_call_args[0],
        second_call_args[1],
        second_call_args[2:],
    )
    assert seconds == 30

    aviasales_api.get_cheapest_ticket.return_value = None
    await scheduled_fn(*scheduled_fn_args)
    aviasales_api.get_cheapest_ticket.assert_awaited_with(direction)
    bot.send_message.assert_not_awaited()


def schedule_ticket_check(
    mocker, db, direction, ticket_price_checker_config, check_interval: int = 60
):
    bot = mocker.Mock()
    bot.send_message = AsyncMock()
    aviasales_api = mocker.Mock()
    aviasales_api.get_cheapest_ticket = AsyncMock()
    scheduler = mocker.MagicMock()
    schedule_every_minutes = mocker.MagicMock()
    scheduler.schedule_every_minutes = schedule_every_minutes
    checker = TicketPriceChecker(
        bot, aviasales_api, db, scheduler, ticket_price_checker_config
    )
    assert aviasales_api.mock_calls == []

    user_id = 1
    checker.schedule_check(user_id, direction)
    assert schedule_every_minutes.call_count == 1
    scheduler_call_args = schedule_every_minutes.call_args[0]
    minutes, scheduled_fn, scheduled_fn_args = (
        scheduler_call_args[0],
        scheduler_call_args[1],
        scheduler_call_args[2:],
    )
    assert minutes == check_interval

    async def scheduled_check():
        await scheduled_fn(*scheduled_fn_args)

    return bot.send_message, aviasales_api, scheduled_check


@pytest.mark.parametrize(
    "direction", [FLIGHT_DIRECTION_NO_RETURN, FLIGHT_DIRECTION_WITH_RETURN]
)
@pytest.mark.ticket_price_checker_config_values(
    {
        "check_interval": 30,
        "check_interval_units": "minutes",
        "price_reduction_threshold_percents": 10,
    }
)
@patch(
    "air_bot.checker.ticket_price_checker.print_ticket",
    Mock(return_value="printed ticket"),
)
async def test_schedule_check_receive_tickets_then_lower_price_below_threshold(
    ticket_price_checker_config, db, mocker, direction
):
    bot_send_message, aviasales_api, scheduled_check = schedule_ticket_check(
        mocker, db, direction, ticket_price_checker_config, check_interval=30
    )
    aviasales_api.get_cheapest_ticket.return_value = {"price": 100}
    await scheduled_check()
    aviasales_api.get_cheapest_ticket.assert_awaited_with(direction)
    assert bot_send_message.await_count == 2

    aviasales_api.get_cheapest_ticket.return_value = {"price": 90}
    await scheduled_check()
    aviasales_api.get_cheapest_ticket.assert_awaited_with(direction)
    assert aviasales_api.get_cheapest_ticket.await_count == 2
    # New message to user (price went down below threshold)
    assert bot_send_message.await_count == 4

    aviasales_api.get_cheapest_ticket.return_value = {"price": 110}
    await scheduled_check()
    aviasales_api.get_cheapest_ticket.assert_awaited_with(direction)
    assert aviasales_api.get_cheapest_ticket.await_count == 3
    # No message to user
    assert bot_send_message.await_count == 4

    aviasales_api.get_cheapest_ticket.return_value = {"price": 95}
    await scheduled_check()
    aviasales_api.get_cheapest_ticket.assert_awaited_with(direction)
    assert aviasales_api.get_cheapest_ticket.await_count == 4
    # New message to user (price went down below threshold)
    assert bot_send_message.await_count == 6


@pytest.mark.parametrize(
    "direction", [FLIGHT_DIRECTION_NO_RETURN, FLIGHT_DIRECTION_WITH_RETURN]
)
@pytest.mark.ticket_price_checker_config_values(
    {"price_reduction_threshold_percents": 20}
)
@patch(
    "air_bot.checker.ticket_price_checker.print_ticket",
    Mock(return_value="printed ticket"),
)
async def test_schedule_check_then_prise_declines_slowly(
    ticket_price_checker_config, db, mocker, direction
):
    bot_send_message, aviasales_api, scheduled_check = schedule_ticket_check(
        mocker, db, direction, ticket_price_checker_config
    )

    aviasales_api.get_cheapest_ticket.return_value = {"price": 100}
    await scheduled_check()
    aviasales_api.get_cheapest_ticket.assert_awaited_with(direction)
    assert bot_send_message.await_count == 2

    aviasales_api.get_cheapest_ticket.return_value = {"price": 90}
    await scheduled_check()
    aviasales_api.get_cheapest_ticket.assert_awaited_with(direction)
    assert aviasales_api.get_cheapest_ticket.await_count == 2
    # No new messages to user (because 90 > 100*(1-0.2))
    assert bot_send_message.await_count == 2

    aviasales_api.get_cheapest_ticket.return_value = {"price": 79}
    await scheduled_check()
    aviasales_api.get_cheapest_ticket.assert_awaited_with(direction)
    assert aviasales_api.get_cheapest_ticket.await_count == 3
    # No new messages to user (because 79 > 90*(1-0.2))
    assert bot_send_message.await_count == 2
