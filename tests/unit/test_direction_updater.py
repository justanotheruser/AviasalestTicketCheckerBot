import random
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest
from fakes import FakeUnitOfWork

from air_bot.domain.model import Ticket
from air_bot.service.direction_updater import update
from air_bot.settings import (
    DirectionUpdaterSettings,
    Interval,
    NotificationsSettings,
    SchedulerSetting,
    Settings,
)


def get_tickets(prices, roundtrip=False) -> list[Ticket]:
    result = []
    for price in prices:
        if roundtrip:
            ticket = Ticket(
                price=price,
                departure_at=datetime.now(),
                duration_to=timedelta(minutes=random.randint(30, 600)),
                return_at=datetime.now(),
                duration_back=timedelta(minutes=random.randint(30, 600)),
                link="link",
            )
        else:
            ticket = Ticket(
                price=price,
                departure_at=datetime.now(),
                duration_to=timedelta(minutes=random.randint(30, 600)),
                link="link",
            )
        result.append(ticket)
    return result


class FakeBotService:
    def __init__(self):
        self.notify_user = AsyncMock()


@pytest.mark.asyncio
async def test_notify_subscribed_users_if_new_price_below_threshold(
    moscow2spb_one_way_direction,
):
    uow = FakeUnitOfWork()
    last_update = datetime.now() - timedelta(minutes=61)
    await uow.flight_directions.add_direction_info(
        moscow2spb_one_way_direction, 100, last_update
    )
    direction_id = await uow.flight_directions.get_direction_id(
        moscow2spb_one_way_direction
    )
    await uow.users_directions.add(user_id=1, direction_id=direction_id)
    await uow.users_directions.add(user_id=2, direction_id=direction_id)
    tickets = get_tickets([89, 100, 120])
    aviasales_api = Mock(get_tickets=AsyncMock(return_value=tickets))
    bot = FakeBotService()
    settings = make_settings()
    await update(uow, aviasales_api, bot, settings)
    assert bot.notify_user.call_count == 2
    notify_call_args = [
        bot.notify_user.call_args_list[i].args
        for i in range(bot.notify_user.call_count)
    ]
    assert (1, tickets, moscow2spb_one_way_direction) in notify_call_args
    assert (2, tickets, moscow2spb_one_way_direction) in notify_call_args


def make_settings() -> Settings:
    scheduler = SchedulerSetting(5, Interval.MINUTES)
    direction_updater = DirectionUpdaterSettings(
        needs_update_after=60, max_directions_for_single_update=2
    )
    notifications = NotificationsSettings(price_reduction_threshold_percents=10)
    settings = Settings(
        scheduler=scheduler,
        direction_updater=direction_updater,
        notifications=notifications,
    )
    return settings
