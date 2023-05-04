from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from air_bot.checker.ticket_price_checker import TicketPriceChecker


class AddTicketPriceChecker(BaseMiddleware):
    def __init__(self, ticket_price_checker: TicketPriceChecker):
        self.ticket_price_checker = ticket_price_checker
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["ticket_price_checker"] = self.ticket_price_checker
        return await handler(event, data)
