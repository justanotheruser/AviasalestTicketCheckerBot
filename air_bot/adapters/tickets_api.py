import asyncio
import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Tuple

from aiohttp import ClientConnectionError, ClientSession
from async_timeout import timeout
from loguru import logger
from pydantic import SecretStr

from air_bot.domain.model import FlightDirection, Ticket


class AbstractTicketsApi(ABC):
    @abstractmethod
    async def get_tickets(
        self, direction: FlightDirection, limit: int
    ) -> Tuple[list[Ticket], bool]:
        """Returns 'limit' cheapest tickets for 'direction'. Second return value is True on success,
        False otherwise"""
        raise NotImplementedError


class AviasalesTicketsApi(AbstractTicketsApi):
    def __init__(
        self, session: ClientSession, token: SecretStr, currency: str
    ) -> object:
        self.session = session
        self.token = token
        self.currency = currency

    async def get_tickets(
        self, direction: FlightDirection, limit: int = 3
    ) -> Tuple[list[Ticket], bool]:
        is_direct = "false" if direction.with_transfer else "true"
        try:
            async with timeout(10):
                response = await get_tickets_response(
                    self.session,
                    self.token.get_secret_value(),
                    direction.start_code,
                    direction.end_code,
                    direction.departure_at,
                    direction.return_at,
                    is_direct,
                    limit,
                    self.currency,
                )
        except asyncio.TimeoutError:
            # TODO: logging
            return [], False
        except ClientConnectionError as e:
            logger.error(e)

        json_response = json.loads(response)
        if "error" in response:
            logger.error(
                f'Failed to get tickets: error {json_response["error"]}, direction {direction}'
            )
            return [], False
        if "data" not in json_response:
            logger.error(f"Unexpected response from Aviasales: {json_response}")
            return [], False
        return parse_tickets(json_response["data"]), True


async def get_tickets_response(
    session: ClientSession,
    token: str,
    start_code: str,
    end_code: str,
    departure_date: str,
    return_date: str | None,
    is_direct: str,
    limit: int,
    currency: str,
) -> str:
    travel_payouts_url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
    params = {
        "origin": start_code,
        "destination": end_code,
        "departure_at": departure_date,
        "direct": is_direct,
        "limit": limit,
        "currency": currency,
        "sorting": "price",
        "token": token,
    }
    if return_date:
        params["return_at"] = return_date
    async with session.get(travel_payouts_url, params=params) as response:
        return await response.text()


def parse_tickets(json_tickets) -> list[Ticket]:
    result = []
    for json_ticket in json_tickets:
        price = float(json_ticket["price"])
        departure_at = datetime_from_ticket(json_ticket["departure_at"])
        duration_to = timedelta(minutes=json_ticket["duration_to"])
        if "return_at" in json_ticket:
            return_at = datetime_from_ticket(json_ticket["return_at"])
            duration_back = timedelta(minutes=json_ticket["duration_back"])
        else:
            return_at = None
            duration_back = None
        result.append(
            Ticket(
                price=price,
                departure_at=departure_at,
                return_at=return_at,
                duration_to=duration_to,
                duration_back=duration_back,
                link=json_ticket["link"],
            )
        )
    return result


def datetime_from_ticket(datetime_str: str) -> datetime:
    """Converts datetime from string in Aviasales API response to Python's datetime; ditches timezone"""
    return datetime.strptime(
        str(datetime_str)[: len(datetime_str) - 9], "%Y-%m-%dT%H:%M"
    )
