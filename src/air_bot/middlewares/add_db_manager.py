from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from air_bot.db.db_manager import DBManager


class AddDBManager(BaseMiddleware):
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["db_manager"] = self.db_manager
        return await handler(event, data)
