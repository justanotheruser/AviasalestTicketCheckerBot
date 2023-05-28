import asyncio
import logging
from typing import Optional

from aiohttp import ClientSession, ClientConnectionError

logger = logging.getLogger(__name__)


async def get_tickets_response(
    session: ClientSession,
    token: str,
    start_code: str,
    end_code: str,
    departure_date: str,
    return_date: Optional[str],
    is_direct: str,
    limit: int,
) -> str:
    travel_payouts_url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
    params = {
        "origin": start_code,
        "destination": end_code,
        "departure_at": departure_date,
        "direct": is_direct,
        "limit": limit,
        "currency": "rub",
        "sorting": "price",
        "token": token,
    }
    if return_date:
        params["return_at"] = return_date
    try:
        async with session.get(travel_payouts_url, params=params) as response:
            return await response.text()
    except ClientConnectionError as e:
        logging.error(
            f"ClientConnectionError: url={travel_payouts_url}, params={params}", {e}
        )
        raise asyncio.TimeoutError()
