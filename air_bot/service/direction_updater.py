from datetime import datetime, timedelta

from loguru import logger

from air_bot.adapters.repo.session_maker import SessionMaker
from air_bot.adapters.repo.uow import AbstractUnitOfWork, SqlAlchemyUnitOfWork
from air_bot.adapters.tickets_api import AbstractTicketsApi, AviasalesTicketsApi
from air_bot.bot.service import BotService
from air_bot.domain.exceptions import (
    TicketsAPIConnectionError,
    TicketsAPIError,
    TicketsParsingError,
)
from air_bot.domain.model import FlightDirectionInfo, Ticket
from air_bot.settings import Settings, SettingsStorage, UsersSettings


class DirectionUpdater:
    def __init__(
        self,
        settings_storage: SettingsStorage,
        bot: BotService,
        session_maker: SessionMaker,
        http_session_maker,
    ):
        self.settings_storage = settings_storage
        self.bot = bot
        self.session_maker = session_maker
        self.http_session_maker = http_session_maker

    async def update(self):
        uow = SqlAlchemyUnitOfWork(self.session_maker)
        aviasales_api = AviasalesTicketsApi(self.http_session_maker)
        await update(uow, aviasales_api, self.bot, self.settings_storage.settings)

    async def remove_outdated(self):
        """Removes directions with a past departure date"""
        uow = SqlAlchemyUnitOfWork(self.session_maker)
        async with uow:
            await uow.flight_directions.delete_outdated_directions()
            await uow.commit()


async def update(
    uow: AbstractUnitOfWork, aviasales_api: AbstractTicketsApi, bot, settings: Settings
):
    logger.info("Starting direction update")
    update_threshold = datetime.now() - timedelta(
        minutes=settings.direction_updater.needs_update_after
    )
    async with uow:
        directions = await uow.flight_directions.get_directions_with_last_update_before(
            update_threshold,
            settings.direction_updater.max_directions_for_single_update,
        )
        await uow.commit()
    for direction in directions:
        await _update_direction(uow, aviasales_api, bot, settings, direction)


async def _update_direction(
    uow: AbstractUnitOfWork,
    aviasales_api: AbstractTicketsApi,
    bot,
    settings: Settings,
    direction_info: FlightDirectionInfo,
):
    update_timestamp = datetime.now()
    try:
        tickets = await aviasales_api.get_tickets(direction_info.direction, limit=3)
    except (TicketsAPIConnectionError, TicketsAPIError, TicketsParsingError):
        return
    if tickets:
        cheapest_price = tickets[0].price
    else:
        cheapest_price = None
    last_price = direction_info.price
    direction_info.price = cheapest_price

    async with uow:
        await uow.tickets.remove_for_direction(direction_info.id)
        await uow.tickets.add(tickets, direction_info.id)
        await uow.flight_directions.update_price(
            direction_info.id, cheapest_price, update_timestamp
        )
        await uow.commit()

    await _notify_users(uow, bot, settings.users, direction_info, last_price, tickets)


async def _notify_users(
    uow: AbstractUnitOfWork,
    bot,
    settings: UsersSettings,
    direction_info: FlightDirectionInfo,
    last_price: float | None,
    tickets: list[Ticket],
):
    if not _users_need_notification(settings, last_price, tickets):
        return
    async with uow:
        user_ids = await uow.users_directions.get_users(direction_info.id)
        await uow.commit()
    for user_id in user_ids:
        await bot.notify_user(user_id, tickets, direction_info.direction)


def _users_need_notification(
    settings: UsersSettings, last_price: float | None, tickets: list[Ticket]
) -> bool:
    if len(tickets) == 0:
        return False
    cheapest_ticket = tickets[0]
    notification_threshold = last_price * (
        1 - settings.price_reduction_threshold_percents / 100
    )
    return not last_price or cheapest_ticket.price <= notification_threshold
