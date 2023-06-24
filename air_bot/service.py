import datetime
from abc import ABC, abstractmethod

from air_bot.adapters.tickets_api import AbstractTicketsApi
from air_bot.domain.exceptions import InternalError, TicketsError, TicketsParsingError
from air_bot.domain.model import FlightDirection, Ticket, FlightDirectionInfo
from air_bot.adapters.repo.uow import AbstractUnitOfWork


N_CHEAPEST_TICKETS_FOR_NEW_DIRECTION = 3


async def track(user_id: int, direction: FlightDirection, tickets_api: AbstractTicketsApi, uow: AbstractUnitOfWork) -> list[Ticket] | None:
    """Adds new direction to directions tracked by user with user_id. Returns list of cheapest
    tickets for this direction or None if request to Aviasales API failed for some reason.
    If direction is already in DB, returns tickets from DB."""
    direction_id = await uow.flight_directions.get_direction_id(direction)
    if direction_id:
        # TODO: make this foreign keys in real DB schema; also make sure you check this table
        # for presence of direction_id and delete from it in single transaction
        success = await uow.users_directions.add(user_id, direction_id)
        if not success:
            return []
        tickets, success = await uow.tickets.get_direction_tickets(
            direction_id
        )
        if not tickets or not success:
            return []

    try:
        tickets = await tickets_api.get_tickets(direction, limit=3)
    except TicketsParsingError:
        raise InternalError()
    except TicketsError:
        tickets = None

    cheapest_price = tickets[0].price if tickets else None
    async with uow:
        await uow.flight_directions.add_direction_info(
            direction, cheapest_price, datetime.datetime.now()
        )
        await uow.users_directions.add(user_id, direction_id)
        if tickets:
            await uow.tickets.add(tickets, direction_id)
        await uow.commit()

    return tickets


async def get_user_directions(user_id: int, uow: AbstractUnitOfWork) -> list[FlightDirectionInfo]:
    async with uow:
        direction_ids = await uow.users_directions.get_user_directions(user_id)
        if not direction_ids:
            return []
        return await uow.flight_directions.get_directions_info(direction_ids)
