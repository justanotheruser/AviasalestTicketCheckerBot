from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from air_bot.bot.i18n import Translator


class AddTranslatorMiddleware(BaseMiddleware):
    def __init__(self, translator: Translator):
        super().__init__()
        self.translator = translator

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["translator"] = self.translator
        return await handler(event, data)
