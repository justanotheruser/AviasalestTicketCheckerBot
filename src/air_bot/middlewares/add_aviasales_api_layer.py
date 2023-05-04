from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from air_bot.aviasales_api.api_layer import AviasalesAPILayer


class AddAviasalesAPILayerMiddleware(BaseMiddleware):
    def __init__(self, aviasales_api: AviasalesAPILayer):
        self.aviasales_api = aviasales_api
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["aviasales_api"] = self.aviasales_api
        return await handler(event, data)
