import asyncio
import json
from abc import ABC, abstractmethod

from aiohttp import ClientConnectionError, ClientSession
from async_timeout import timeout
from loguru import logger

from air_bot.domain.exceptions import (
    LocationsApiConnectionError,
    LocationsApiRespondedWithError,
)
from air_bot.domain.model import Location


class AbstractLocationsApi(ABC):
    @abstractmethod
    async def get_locations(self, airport_or_city: str) -> list[Location]:
        raise NotImplementedError


class TravelPayoutsLocationsApi(AbstractLocationsApi):
    def __init__(self, session: ClientSession, locale: str):
        self.session = session
        self.locale = locale

    async def get_locations(self, airport_or_city: str) -> list[Location]:
        response = await get_locations_response(
            self.session, self.locale, airport_or_city
        )
        json_response = json.loads(response)
        if "error" in response:
            logger.error(
                f'Location API responded with error {json_response["error"]}, '
                f"airport_or_city {airport_or_city}"
            )
            raise LocationsApiRespondedWithError()
        return parse_locations(json_response)


PLACES_ENDPOINT_URL = "https://autocomplete.travelpayouts.com/places2"
REQUEST_TIMEOUT = 10


async def get_locations_response(
    session: ClientSession, locale: str, airport_or_city: str
) -> str:
    params = {"locale": locale, "types[]": ["airport", "city"], "term": airport_or_city}
    try:
        async with timeout(REQUEST_TIMEOUT):
            async with session.get(PLACES_ENDPOINT_URL, params=params) as response:
                return await response.text()
    except ClientConnectionError as e:
        logger.error(f"ClientConnectionError: {e}, params={params}")
        raise LocationsApiConnectionError()
    except asyncio.TimeoutError:
        logger.error(
            f"Locations endpoint did not respond in {REQUEST_TIMEOUT} seconds, "
            f"params={params}"
        )
        raise LocationsApiConnectionError()


def parse_locations(json_response):
    first_country_code = None
    locations = []
    for i in json_response:
        if not first_country_code:
            first_country_code = i["country_code"]
        if i["country_code"] != first_country_code:
            continue
        locations.append(
            Location(
                code=i["code"],
                name=i["name"],
                country_code=i["country_code"],
            )
        )
    return locations
