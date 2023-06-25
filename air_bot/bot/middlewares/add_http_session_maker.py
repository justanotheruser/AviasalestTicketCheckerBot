from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from air_bot.http_session import HttpSessionMaker


class AddHttpSessionMakerMiddleware(BaseMiddleware):
    def __init__(self, http_session_maker: HttpSessionMaker):
        super().__init__()
        self.http_session_maker = http_session_maker

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["http_session_maker"] = self.http_session_maker
        return await handler(event, data)
