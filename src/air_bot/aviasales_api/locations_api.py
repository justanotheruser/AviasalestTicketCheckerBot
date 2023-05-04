import asyncio
import logging

from aiohttp import ClientSession, ClientConnectionError

logger = logging.getLogger("AirBot")


async def get_locations_response(session: ClientSession, airport_or_city: str) -> str:
    travel_payouts_url = "https://autocomplete.travelpayouts.com/places2"
    params = {"locale": "ru", "types[]": ["airport", "city"], "term": airport_or_city}
    try:
        async with session.get(travel_payouts_url, params=params) as response:
            return await response.text()
    except ClientConnectionError as e:
        logger.error(
            f"ClientConnectionError: url={travel_payouts_url}, params={params}", {e}
        )
        raise asyncio.TimeoutError()
