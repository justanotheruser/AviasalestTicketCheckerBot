from datetime import datetime, timedelta

from aiogram.exceptions import TelegramAPIError
from loguru import logger

from air_bot.adapters.repo.session_maker import SessionMaker
from air_bot.adapters.repo.uow import AbstractUnitOfWork, SqlAlchemyUnitOfWork
from air_bot.adapters.tickets_api import AbstractTicketsApi, AviasalesTicketsApi
from air_bot.domain.exceptions import (
    TicketsAPIConnectionError,
    TicketsAPIError,
    TicketsParsingError,
)
from air_bot.domain.model import FlightDirectionInfo, Ticket
from air_bot.domain.ports.user_notifier import UserNotifier
from air_bot.settings import Settings, SettingsStorage, UsersSettings


class DirectionUpdater:
    def __init__(
        self,
        settings_storage: SettingsStorage,
        session_maker: SessionMaker,
        http_session_maker,
    ):
        self.settings_storage = settings_storage
        self.user_notifier: UserNotifier | None = None
        self.session_maker = session_maker
        self.http_session_maker = http_session_maker

    def set_user_notifier(self, bot: UserNotifier):
        self.user_notifier = bot

    async def update(self):
        try:
            uow = SqlAlchemyUnitOfWork(self.session_maker)
            aviasales_api = AviasalesTicketsApi(self.http_session_maker)
            await update(
                uow, aviasales_api, self.user_notifier, self.settings_storage.settings
            )
        except Exception as e:
            logger.error(e)

    async def remove_outdated(self) -> int:
        """Returns number of removed directions with a past departure date"""
        logger.info("Removing outdated directions")
        uow = SqlAlchemyUnitOfWork(self.session_maker)
        async with uow:
            n_directions = await uow.flight_directions.delete_outdated_directions()
            await uow.commit()
        logger.info(f"Number of removed outdated directions: {n_directions}")
        return n_directions


async def update(
    uow: AbstractUnitOfWork,
    aviasales_api: AbstractTicketsApi,
    user_notifier: UserNotifier | None,
    settings: Settings,
):
    logger.info("Checking if some directions need update")
    update_threshold = datetime.now() - timedelta(
        minutes=settings.direction_updater.needs_update_after
    )
    async with uow:
        directions = await uow.flight_directions.get_directions_with_last_update_before(
            update_threshold,
            settings.direction_updater.max_directions_for_single_update,
        )
        await uow.commit()
    logger.info(f"{len(directions)} direction(s) need update")
    for direction in directions:
        await _update_direction(uow, aviasales_api, user_notifier, settings, direction)


async def _update_direction(
    uow: AbstractUnitOfWork,
    aviasales_api: AbstractTicketsApi,
    user_notifier: UserNotifier | None,
    settings: Settings,
    direction_info: FlightDirectionInfo,
):
    logger.info(f"Updating info about direction {direction_info.id}")
    update_timestamp = datetime.now()
    try:
        tickets = await aviasales_api.get_tickets(direction_info.direction, limit=3)
    except (TicketsAPIConnectionError, TicketsAPIError, TicketsParsingError):
        return
    if tickets:
        logger.info(f"Received tickets for direction {direction_info.id}")
        cheapest_price = tickets[0].price
    else:
        cheapest_price = None
        logger.info(f"Received no tickets for direction {direction_info.id}")
    last_price = direction_info.price
    direction_info.price = cheapest_price

    assert direction_info.id is not None
    async with uow:
        await uow.tickets.remove_for_direction(direction_info.id)
        await uow.tickets.add(tickets, direction_info.id)
        await uow.flight_directions.update_price(
            direction_info.id, cheapest_price, update_timestamp
        )
        await uow.commit()

    if user_notifier is None:
        logger.warning("Can't notify users after update - bot was not set yet")
        return
    await _notify_users(
        uow, user_notifier, settings.users, direction_info, last_price, tickets
    )


async def _notify_users(
    uow: AbstractUnitOfWork,
    user_notifier: UserNotifier,
    settings: UsersSettings,
    direction_info: FlightDirectionInfo,
    last_price: float | None,
    tickets: list[Ticket],
):
    assert direction_info.id is not None
    if not _users_need_notification(settings, last_price, tickets):
        logger.info("No notifications needed", direction_id=direction_info.id)
        return
    async with uow:
        user_ids = await uow.users_directions.get_users(direction_info.id)
        await uow.commit()
    logger.info(
        f"Sending notifications about new price for direction {direction_info.id} to {len(user_ids)} user(s)",
        user_ids=user_ids,
    )
    for user_id in user_ids:
        # TODO make this parallel!
        logger.info(
            "Sending price update notification to user",
            user_id=user_id,
            direction_id=direction_info.id,
        )
        try:
            await user_notifier.notify_user(
                user_id, tickets, direction_info.direction, direction_info.id
            )
        except TelegramAPIError:
            # TODO: remove user in case of TelegramForbiddenError (bot was blocked by user)
            pass


def _users_need_notification(
    settings: UsersSettings, last_price: float | None, tickets: list[Ticket]
) -> bool:
    if len(tickets) == 0:
        return False
    cheapest_ticket = tickets[0]
    if last_price is None:
        return True
    notification_threshold = last_price * (
        1 - settings.price_reduction_threshold_percents / 100
    )
    return cheapest_ticket.price <= notification_threshold
