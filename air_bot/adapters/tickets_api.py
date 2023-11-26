import asyncio
import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from aiohttp import ClientConnectionError, ClientSession
from async_timeout import timeout
from loguru import logger

from air_bot.config import config
from air_bot.domain.exceptions import (
    TicketsAPIConnectionError,
    TicketsAPIError,
    TicketsParsingError,
)
from air_bot.domain.model import FlightDirection, Ticket


class AbstractTicketsApi(ABC):
    @abstractmethod
    async def get_tickets(self, direction: FlightDirection, limit: int) -> list[Ticket]:
        """Returns 'limit' cheapest tickets for 'direction' ordered by price"""
        raise NotImplementedError

    @abstractmethod
    async def get_cheapest_tickets_for_month(
        self, direction: FlightDirection, departure_year: int, departure_month: int
    ) -> dict[str, Ticket]:
        raise NotImplementedError


class AviasalesTicketsApi(AbstractTicketsApi):
    def __init__(self, http_session_maker):
        self.session = http_session_maker()
        self.token = config.aviasales_api_token
        self.currency = config.currency

    async def get_tickets(
        self, direction: FlightDirection, limit: int = 3
    ) -> list[Ticket]:
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
            logger.error("Request for tickets timed out")
            raise TicketsAPIConnectionError()
        except ClientConnectionError as e:
            logger.error(e)
            raise TicketsAPIConnectionError()

        json_response = json.loads(response)
        if "error" in response:
            logger.error(
                f'Failed to get tickets: error {json_response["error"]}, direction {direction}'
            )
            raise TicketsAPIError()
        return parse_tickets(json_response)

    async def get_cheapest_tickets_for_month(
        self, direction: FlightDirection, departure_year: int, departure_month: int
    ) -> dict[str, Ticket]:
        is_direct = "false" if direction.with_transfer else "true"
        try:
            async with timeout(10):
                response = await get_grouped_prices(
                    self.session,
                    self.token.get_secret_value(),
                    self.currency,
                    direction.start_code,
                    direction.end_code,
                    direction.departure_at,
                    direction.return_at,
                    is_direct,
                )
        except asyncio.TimeoutError:
            logger.error("Request for cheapest tickets for month timed out")
            raise TicketsAPIConnectionError()
        except ClientConnectionError as e:
            logger.error(e)
            raise TicketsAPIConnectionError()
        json_response = json.loads(response)
        if "error" in response:
            logger.error(
                f'Failed to get tickets: error {json_response["error"]}, direction {direction}'
            )
            raise TicketsAPIError()
        return parse_tickets_by_date(json_response)


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


def parse_tickets(json_response) -> list[Ticket]:
    if "data" not in json_response:
        logger.error(f"Unexpected response from Aviasales: {json_response}")
        raise TicketsParsingError()
    json_tickets = json_response["data"]
    try:
        return [parse_ticket(json_ticket) for json_ticket in json_tickets]
    except Exception:
        raise TicketsParsingError()


def parse_ticket(json_ticket) -> Ticket:
    price = float(json_ticket["price"])
    departure_at = datetime_from_ticket(json_ticket["departure_at"])
    duration_to = timedelta(minutes=json_ticket["duration_to"])
    if "return_at" in json_ticket:
        return_at = datetime_from_ticket(json_ticket["return_at"])
        duration_back = timedelta(minutes=json_ticket["duration_back"])
    else:
        return_at = None
        duration_back = None
    return Ticket(
        price=price,
        departure_at=departure_at,
        return_at=return_at,
        duration_to=duration_to,
        duration_back=duration_back,
        link=json_ticket["link"],
    )


def datetime_from_ticket(datetime_str: str) -> datetime:
    """Converts datetime from string in Aviasales API response to Python's datetime; ditches timezone"""
    return datetime.strptime(
        str(datetime_str)[: len(datetime_str) - 9], "%Y-%m-%dT%H:%M"
    )


async def get_grouped_prices(
    session: ClientSession,
    token: str,
    currency: str,
    origin: str,
    destination: str,
    departure_at: str,
    return_at: str | None,
    is_direct: str,
    group_by: str = "departure_at",
):
    travel_payouts_url = "https://api.travelpayouts.com/aviasales/v3/grouped_prices"
    params = {
        "token": token,
        "currency": currency,
        "origin": origin,
        "destination": destination,
        "departure_at": departure_at,
        "direct": is_direct,
        "group_by": group_by,
    }
    if return_at:
        params["return_at"] = return_at
    async with session.get(travel_payouts_url, params=params) as response:
        return await response.text()


def parse_tickets_by_date(json_response) -> dict[str, Ticket]:
    if "data" not in json_response:
        logger.error(f"Unexpected response from Aviasales: {json_response}")
        raise TicketsParsingError()
    result = dict()
    try:
        for date, json_ticket in json_response["data"].items():
            result[date] = parse_ticket(json_ticket)
    except Exception:
        raise TicketsParsingError()
    return result
