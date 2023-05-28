import json
import logging
import typing
from typing import Any, Tuple

from aiohttp import ClientSession
from pydantic import SecretStr

from air_bot.aviasales_api.grouped_prices import get_grouped_prices
from air_bot.aviasales_api.locations_api import get_locations_response
from air_bot.aviasales_api.tickets_api import get_tickets_response
from air_bot.bot_types import FlightDirection
from air_bot.bot_types import Location, LocationType

logger = logging.getLogger(__name__)


class AviasalesAPILayer:
    def __init__(self, session: ClientSession, token: SecretStr):
        self.session = session
        self.token = token

    async def get_locations(self, airport_or_city: str) -> list[Location]:
        response = await get_locations_response(self.session, airport_or_city)
        json_response = json.loads(response)
        first_country_code = None
        locations = []
        for i in json_response:
            if not first_country_code:
                first_country_code = i["country_code"]
            if i["country_code"] != first_country_code:
                continue
            type_ = (
                LocationType.AIRPORT if i["type"] == "airport" else LocationType.CITY
            )
            locations.append(
                Location(
                    type_=type_,
                    code=i["code"],
                    name=i["name"],
                    country_code=i["country_code"],
                )
            )
        return locations

    async def get_tickets(self, direction: FlightDirection, limit: int = 3) -> Any:
        is_direct = "false" if direction.with_transfer else "true"
        response = await get_tickets_response(
            self.session,
            self.token.get_secret_value(),
            direction.start_code,
            direction.end_code,
            direction.departure_at,
            direction.return_at,
            is_direct,
            limit,
        )
        json_response = json.loads(response)
        if "error" in response:
            logger.error(
                f'Failed to get tickets: error {json_response["error"]}, direction {direction}'
            )
            return None
        if not json_response["data"]:
            return []
        return json_response["data"]

    async def get_cheapest_ticket(self, direction: FlightDirection) -> Tuple[Any, bool]:
        """Returns the cheapest ticket (or None if there's no tickets).
        Second return value is True if request was successful."""
        if does_include_day(direction.departure_at):
            group_by = "departure_at"
        else:
            group_by = "month"
        response = await get_grouped_prices(
            self.session, self.token.get_secret_value(), direction, group_by=group_by
        )
        if response is None:
            return None, False
        if not response["data"]:
            return None, True
        return response["data"][direction.departure_at], True

    async def get_cheapest_tickets_for_month(
        self, direction: FlightDirection, departure_year: int, departure_month: int
    ) -> typing.Tuple[dict[str, Any], bool]:
        direction.departure_at = f"{departure_year}-{departure_month:02d}"
        response = await get_grouped_prices(
            self.session, self.token.get_secret_value(), direction
        )
        if response is None:
            return dict(), False
        return response["data"], True


def does_include_day(date_str: str) -> bool:
    return len(date_str) > 7
