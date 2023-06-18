from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from air_bot.adapters.locations_api import TravelPayoutsLocationsApi


class AddLocationsApiMiddleware(BaseMiddleware):
    def __init__(self, locations_api: TravelPayoutsLocationsApi):
        super().__init__()
        self.locations_api = locations_api

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["locations_api"] = self.locations_api
        return await handler(event, data)
