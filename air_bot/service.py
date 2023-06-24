import datetime

import asyncmy.errors
from loguru import logger

from air_bot.adapters.repo.uow import AbstractUnitOfWork
from air_bot.adapters.tickets_api import AbstractTicketsApi
from air_bot.domain.exceptions import InternalError, TicketsError, TicketsParsingError
from air_bot.domain.model import FlightDirection, FlightDirectionInfo, Ticket

N_CHEAPEST_TICKETS_FOR_NEW_DIRECTION = 3


async def add_user(user_id: int, uow: AbstractUnitOfWork):
    async with uow:
        try:
            await uow.users.add(user_id)
            await uow.commit()
        except asyncmy.errors.IntegrityError:
            # User already in repo
            pass
        except Exception as e:
            logger.error(e)


async def track(
    user_id: int,
    direction: FlightDirection,
    tickets_api: AbstractTicketsApi,
    uow: AbstractUnitOfWork,
) -> list[Ticket] | None:
    """Adds new direction to directions tracked by user with user_id. Returns list of cheapest
    tickets for this direction or None if request to Aviasales API failed for some reason.
    If direction is already in DB, returns tickets from DB."""
    tickets = []
    got_tickets_from_api = False
    async with uow:
        direction_id = await uow.flight_directions.get_direction_id(direction)
        if direction_id is not None:
            await uow.users_directions.add(user_id, direction_id)
            tickets = await uow.tickets.get_direction_tickets(direction_id)
        await uow.commit()

    if not tickets:
        try:
            tickets = await tickets_api.get_tickets(direction, limit=3)
            if tickets:
                got_tickets_from_api = True
        except TicketsParsingError:
            raise InternalError()
        except TicketsError:
            tickets = None

    if not tickets:
        if direction_id is None:
            async with uow:
                direction_id = await uow.flight_directions.add_direction_info(
                    direction, None, datetime.datetime.now()
                )
                await uow.users_directions.add(user_id, direction_id)
                await uow.commit()
        return []

    if got_tickets_from_api:
        cheapest_price = tickets[0].price
        async with uow:
            if direction_id is None:
                direction_id = await uow.flight_directions.add_direction_info(
                    direction, cheapest_price, datetime.datetime.now()
                )
                await uow.users_directions.add(user_id, direction_id)
            else:
                await uow.flight_directions.update_price(direction_id, cheapest_price, datetime.datetime.now())
            await uow.tickets.remove_for_direction(direction_id)
            await uow.tickets.add(tickets, direction_id)
            await uow.commit()

    return tickets


async def get_user_directions(
    user_id: int, uow: AbstractUnitOfWork
) -> list[FlightDirectionInfo]:
    async with uow:
        direction_ids = await uow.users_directions.get_directions(user_id)
        if not direction_ids:
            return []
        return await uow.flight_directions.get_directions_info(direction_ids)
