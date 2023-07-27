from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from air_bot.adapters.repo.session_maker import SessionMaker
from air_bot.bot.handlers import (
    add_flight_direction,
    low_prices_calendar,
    start,
    user_profile,
)
from air_bot.bot.keyboards.low_prices_calendar_kb import (
    show_low_prices_calendar_keyboard,
)
from air_bot.bot.middlewares.add_calendar_view import AddCalendarViewMiddleware
from air_bot.bot.middlewares.add_http_session_maker import AddHttpSessionMakerMiddleware
from air_bot.bot.middlewares.add_session_maker import AddSessionMakerMiddleware
from air_bot.bot.middlewares.add_settings_storage import AddSettingsStorageMiddleware
from air_bot.bot.middlewares.add_ticket_view import AddTicketViewMiddleware
from air_bot.bot.presentation.low_price_calendar import CalendarView
from air_bot.bot.presentation.tickets import TicketView
from air_bot.config import BotConfig
from air_bot.domain.model import FlightDirection, Ticket
from air_bot.http_session import HttpSessionMaker
from air_bot.settings import SettingsStorage


class BotService:
    def __init__(
        self,
        config: BotConfig,
        http_session_maker: HttpSessionMaker,
        session_maker: SessionMaker,
        settings_storage: SettingsStorage,
    ):
        self.dp = Dispatcher(storage=MemoryStorage())
        self.bot = Bot(token=config.bot_token.get_secret_value())

        self.dp.include_router(start.router)
        self.dp.include_router(add_flight_direction.router)
        self.dp.include_router(user_profile.router)
        self.dp.include_router(low_prices_calendar.router)

        self.dp.update.middleware(AddSessionMakerMiddleware(session_maker))
        self.dp.update.middleware(AddHttpSessionMakerMiddleware(http_session_maker))
        self.dp.update.middleware(AddSettingsStorageMiddleware(settings_storage))
        self.ticket_view = TicketView(config.currency)
        self.dp.update.middleware(AddTicketViewMiddleware(self.ticket_view))
        self.low_price_calendar_view = CalendarView(config.currency)
        self.dp.update.middleware(
            AddCalendarViewMiddleware(self.low_price_calendar_view)
        )

    async def start(self) -> None:
        await self.dp.start_polling(self.bot)

    async def notify_user(
        self,
        user_id: int,
        tickets: list[Ticket],
        direction: FlightDirection,
        direction_id: int,
    ):
        await self.bot.send_message(
            user_id,
            text=self.ticket_view.print_tickets(tickets, direction),
            parse_mode="html",
            disable_web_page_preview=True,
            reply_markup=show_low_prices_calendar_keyboard(direction_id),
        )
