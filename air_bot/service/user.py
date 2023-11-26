import datetime
from typing import Tuple

from loguru import logger

from air_bot.adapters.repo.uow import AbstractUnitOfWork
from air_bot.adapters.tickets_api import AbstractTicketsApi
from air_bot.domain.model import FlightDirection, FlightDirectionInfo, Ticket
from air_bot.settings import SettingsStorage

N_CHEAPEST_TICKETS_FOR_NEW_DIRECTION = 3


async def add_user(user_id: int, uow: AbstractUnitOfWork):
    try:
        async with uow:
            exists = await uow.users.exists(user_id)
            if not exists:
                logger.info(f"New user {user_id}")
                await uow.users.add(user_id)
                await uow.commit()
    except Exception as e:
        logger.error(e)


async def track(
    user_id: int,
    direction: FlightDirection,
    tickets_api: AbstractTicketsApi,
    uow: AbstractUnitOfWork,
) -> Tuple[list[Ticket], int]:
    """Adds new direction to directions tracked by user with user_id. Returns list of cheapest tickets for this
    direction and direction id (existing or new one if it is the first user tracking this direction).
    If DB already contains tickets for this direction - returns tickets from DB."""
    tickets = []
    got_tickets_from_api = False
    async with uow:
        direction_id = await uow.flight_directions.get_direction_id(direction)
        if direction_id is not None:
            await uow.users_directions.add(user_id, direction_id)
            tickets = await uow.tickets.get_direction_tickets(direction_id)
        await uow.commit()

    if len(tickets) == 0:
        tickets = await tickets_api.get_tickets(
            direction, limit=N_CHEAPEST_TICKETS_FOR_NEW_DIRECTION
        )
        if len(tickets) > 0:
            got_tickets_from_api = True

    if direction_id is None:
        cheapest_price = tickets[0].price if tickets else None
        async with uow:
            direction_id = await uow.flight_directions.add_direction_info(
                direction, cheapest_price, datetime.datetime.now()
            )
            await uow.users_directions.add(user_id, direction_id)
            await uow.tickets.add(tickets, direction_id)
            await uow.commit()
        return tickets, direction_id

    if got_tickets_from_api:
        cheapest_price = tickets[0].price
        async with uow:
            await uow.flight_directions.update_price(
                direction_id, cheapest_price, datetime.datetime.now()
            )
            await uow.tickets.remove_for_direction(direction_id)
            await uow.tickets.add(tickets, direction_id)
            await uow.commit()

    return tickets, direction_id


async def get_user_directions(
    user_id: int, uow: AbstractUnitOfWork
) -> list[FlightDirectionInfo]:
    async with uow:
        direction_ids = await uow.users_directions.get_directions(user_id)
        if not direction_ids:
            return []
        directions = await uow.flight_directions.get_directions_info(direction_ids)
        await uow.commit()
    return directions


async def delete_direction_if_no_longer_tracked(
    uow: AbstractUnitOfWork, direction_id: int
):
    async with uow:
        users = await uow.users_directions.get_users(direction_id)
        if not users:
            await uow.flight_directions.delete_direction(direction_id)
        await uow.commit()


async def check_if_new_tracking_available(
    settings_storage: SettingsStorage, uow: AbstractUnitOfWork, user_id: int
) -> bool:
    max_directions_per_user = settings_storage.settings.users.max_directions_per_user
    async with uow:
        directions = await uow.users_directions.get_directions(user_id)
        if len(directions) >= max_directions_per_user:
            return False
    return True
