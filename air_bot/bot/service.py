from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from air_bot.adapters.repo.session_maker import SessionMaker
from air_bot.bot.handlers import (
    add_flight_direction,
    admin,
    low_prices_calendar,
    start,
    user_profile,
)
from air_bot.bot.keyboards.low_prices_calendar_kb import (
    show_low_prices_calendar_keyboard,
)
from air_bot.bot.middlewares.depends import Depends
from air_bot.bot.presentation.low_price_calendar import CalendarView
from air_bot.bot.presentation.tickets import TicketView
from air_bot.config import BotConfig
from air_bot.domain.model import FlightDirection, Ticket
from air_bot.domain.ports.user_notifier import UserNotifier
from air_bot.http_session import HttpSessionMaker
from air_bot.service.direction_updater import DirectionUpdater
from air_bot.settings import SettingsStorage


class BotService(UserNotifier):
    def __init__(
        self,
        config: BotConfig,
        http_session_maker: HttpSessionMaker,
        session_maker: SessionMaker,
        settings_storage: SettingsStorage,
        direction_updater: DirectionUpdater,
    ):
        self.dp = Dispatcher(storage=MemoryStorage())
        self.bot = Bot(token=config.bot_token.get_secret_value())

        self.dp.include_router(start.router)
        self.dp.include_router(admin.router)
        self.dp.include_router(user_profile.router)
        self.dp.include_router(add_flight_direction.router)
        self.dp.include_router(low_prices_calendar.router)

        self.ticket_view = TicketView(config.currency)
        self.low_price_calendar_view = CalendarView(config.currency)
        handler_dependencies = [
            ("session_maker", session_maker),
            ("http_session_maker", http_session_maker),
            ("settings_storage", settings_storage),
            ("ticket_view", self.ticket_view),
            ("calendar_view", self.low_price_calendar_view),
            ("direction_updater", direction_updater),
        ]
        for arg_name, arg_value in handler_dependencies:
            self.dp.update.middleware(Depends(arg_name, arg_value))

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
