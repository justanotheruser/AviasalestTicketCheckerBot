from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from air_bot.service_layer.tickets_service import AbstractTicketsService


class AddTicketsServiceMiddleware(BaseMiddleware):
    def __init__(self, tickets_service: AbstractTicketsService):
        super().__init__()
        self.tickets_service = tickets_service

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["tickets_service"] = self.tickets_service
        return await handler(event, data)
