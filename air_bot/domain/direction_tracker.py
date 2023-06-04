from air_bot.adapters.repository import AbstractFlightDirectionRepo
from air_bot.adapters.tickets_api import AbstractTicketsApi
from air_bot.model import FlightDirection, FlightDirectionInfo


class DirectionTracker:
    def __init__(
        self, db_repo: AbstractFlightDirectionRepo, tickets_api: AbstractTicketsApi
    ):
        self.db_repo = db_repo
        self.tickets_api = tickets_api

    async def track(self, user_id: int, direction: FlightDirection):
        pass
