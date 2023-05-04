from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery
from aiohttp import ClientSession


class AddAiohttpSessionMiddleware(BaseMiddleware):
    def __init__(self, session: ClientSession):
        self.session = session
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        data["aiohttp_session"] = self.session
        return await handler(event, data)
