import datetime

from air_bot.adapters.repository import (
    AbstractFlightDirectionRepo,
    AbstractTicketRepo,
    AbstractUserDirectionRepo,
)
from air_bot.adapters.tickets_api import AbstractTicketsApi
from air_bot.domain.exceptions import InternalError, TicketsError, TicketsParsingError
from air_bot.domain.model import FlightDirection, Ticket

N_CHEAPEST_TICKETS_FOR_NEW_DIRECTION = 3


class TicketsService:
    def __init__(
        self,
        flight_direction_repo: AbstractFlightDirectionRepo,
        users_directions_repo: AbstractUserDirectionRepo,
        ticket_repo: AbstractTicketRepo,
        tickets_api: AbstractTicketsApi,
    ):
        self.flight_direction_repo = flight_direction_repo
        self.users_directions_repo = users_directions_repo
        self.ticket_repo = ticket_repo
        self.tickets_api = tickets_api

    async def track(
        self, user_id: int, direction: FlightDirection
    ) -> list[Ticket] | None:
        """Adds new direction to directions tracked by user with user_id. Returns list of cheapest
        tickets for this direction or None if request to Aviasales API failed for some reason.
        If direction is already in DB, returns tickets from DB."""
        direction_id = await self.flight_direction_repo.get_direction_id(direction)
        if direction_id:
            # TODO: make this foreign keys in real DB schema; also make sure you check this table
            # for presence of direction_id and delete from it in single transaction
            success = await self.users_directions_repo.add(user_id, direction_id)
            if not success:
                return []
            tickets, success = await self.ticket_repo.get_direction_tickets(
                direction_id
            )
            if not tickets or not success:
                return []

        try:
            tickets = await self.tickets_api.get_tickets(direction, limit=3)
        except TicketsParsingError:
            raise InternalError()
        except TicketsError:
            tickets = None

        cheapest_price = tickets[0].price if tickets else None
        # Start transaction
        success = await self.flight_direction_repo.add_direction_info(
            direction, cheapest_price, datetime.datetime.now()
        )
        if not success:
            return [], False
        success = await self.users_directions_repo.add(user_id, direction_id)
        if not success:
            return [], False
        # End transaction
        if tickets:
            await self.ticket_repo.add(direction_id, tickets)

        return tickets
