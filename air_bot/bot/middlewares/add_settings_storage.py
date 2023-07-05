from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from air_bot.settings import SettingsStorage


class AddSettingsStorageMiddleware(BaseMiddleware):
    def __init__(self, settings_storage: SettingsStorage):
        super().__init__()
        self.settings_storage = settings_storage

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["settings_storage"] = self.settings_storage
        return await handler(event, data)
