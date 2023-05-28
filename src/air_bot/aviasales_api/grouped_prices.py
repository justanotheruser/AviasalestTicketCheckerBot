import asyncio
import json
import logging
from typing import Optional, Any

from aiohttp import ClientSession, ClientConnectionError
from async_timeout import timeout

from air_bot.bot_types import FlightDirection

logger = logging.getLogger(__name__)


async def get_grouped_prices(
    session: ClientSession,
    token: str,
    direction: FlightDirection,
    group_by: str = "departure_at",
    timeout_sec: int = 10,
) -> Optional[dict[str, Any]]:
    travel_payouts_url = "https://api.travelpayouts.com/aviasales/v3/grouped_prices"
    is_direct = "false" if direction.with_transfer else "true"
    params = {
        "origin": direction.start_code,
        "destination": direction.end_code,
        "departure_at": direction.departure_at,
        "direct": is_direct,
        "group_by": group_by,
        "token": token,
    }
    if direction.return_at:
        params["return_at"] = direction.return_at
    try:
        async with timeout(timeout_sec):
            async with session.get(travel_payouts_url, params=params) as response:
                response_text = await response.text()
    except ClientConnectionError as e:
        logger.error(
            f"ClientConnectionError: url={travel_payouts_url}, params={params}", {e}
        )
        return None
    except asyncio.TimeoutError:
        logger.error("get_grouped_prices request timed out")
        return None
    json_response = json.loads(response_text)
    if "success" not in json_response or not json_response["success"]:
        if "error" in json_response:
            logger.error(f"get_grouped_prices got an error response {json_response}")
        else:
            logger.error(
                f"get_grouped_prices got an unexpected response {json_response}"
            )
        return None
    return json_response
