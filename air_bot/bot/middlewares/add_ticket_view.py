from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from air_bot.bot.presentation.tickets import TicketView


class AddTicketViewMiddleware(BaseMiddleware):
    def __init__(self, ticket_view: TicketView):
        super().__init__()
        self.ticket_view = ticket_view

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["ticket_view"] = self.ticket_view
        return await handler(event, data)
