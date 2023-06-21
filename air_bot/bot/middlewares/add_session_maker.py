from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from air_bot.adapters.repo.session_maker import AbstractSessionMaker


class AddSessionMakerMiddleware(BaseMiddleware):
    def __init__(self, session_maker: AbstractSessionMaker):
        super().__init__()
        self.session_maker = session_maker

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["session_maker"] = self.session_maker
        return await handler(event, data)
