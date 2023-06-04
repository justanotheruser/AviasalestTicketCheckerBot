import datetime
from typing import Tuple

from air_bot.adapters.repository import (
    AbstractFlightDirectionRepo,
    AbstractTicketRepo,
    AbstractUserFlightDirectionRepo,
)
from air_bot.adapters.tickets_api import AbstractTicketsApi
from air_bot.domain.model import FlightDirection, FlightDirectionInfo, Ticket

N_CHEAPEST_TICKETS_FOR_NEW_DIRECTION = 3


class TicketsService:
    def __init__(
        self,
        flight_direction_repo: AbstractFlightDirectionRepo,
        users_directions_repo: AbstractUserFlightDirectionRepo,
        ticket_repo: AbstractTicketRepo,
        tickets_api: AbstractTicketsApi,
    ):
        self.flight_direction_repo = flight_direction_repo
        self.users_directions_repo = users_directions_repo
        self.ticket_repo = ticket_repo
        self.tickets_api = tickets_api

    async def track(
        self, user_id: int, direction: FlightDirection
    ) -> Tuple[list[Ticket], bool]:
        """Adds new direction to tracked by user with user_id. Returns list of cheapest tickets for this direction.
        If direction is already in DB, returns tickets from DB; otherwise makes request to Aviasales API and stores tickets
        """
        direction_id = await self.flight_direction_repo.get_direction_id(direction)
        if direction_id:
            # TODO: make this foreign keys in real DB schema; also make sure you check this table
            # for presence of direction_id and delete from it in single transaction
            success = await self.users_directions_repo.add(user_id, direction_id)
            if not success:
                return [], False
            tickets, success = await self.ticket_repo.get_direction_tickets(
                direction_id
            )
            if not tickets or not success:
                return [], False

        tickets = await self.tickets_api.get_tickets(direction, limit=3)
        cheapest_price = tickets[0].price if tickets else None
        direction_info = FlightDirectionInfo(
            id=1,
            direction=direction,
            price=cheapest_price,
            last_update=datetime.datetime.now(),
        )
        # Start transaction
        success = await self.flight_direction_repo.add_direction_info(direction_info)
        if not success:
            return [], False
        success = await self.users_directions_repo.add(user_id, direction_id)
        if not success:
            return [], False
        success = await self.ticket_repo.add(direction_id, tickets)
        if not success:
            return [], False
        # End transaction

        return tickets, True
