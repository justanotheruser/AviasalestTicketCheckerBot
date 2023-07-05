from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from air_bot.bot.presentation.low_price_calendar import CalendarView


class AddCalendarViewMiddleware(BaseMiddleware):
    def __init__(self, calendar_view: CalendarView):
        super().__init__()
        self.calendar_view = calendar_view

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["calendar_view"] = self.calendar_view
        return await handler(event, data)
