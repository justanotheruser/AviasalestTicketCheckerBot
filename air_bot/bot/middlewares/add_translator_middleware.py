from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from air_bot.bot.i18n import Translator


class AddTranslatorMiddleware(BaseMiddleware):
    def __init__(self, i18n: Translator):
        super().__init__()
        self.i18n = i18n

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["i18n"] = self.i18n
        return await handler(event, data)
