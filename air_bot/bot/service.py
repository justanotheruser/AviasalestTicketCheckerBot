import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from air_bot.adapters.repo.session_maker import SessionMaker
from air_bot.bot.handlers import add_flight_direction, start, user_profile
from air_bot.bot.middlewares.add_http_session_maker import AddHttpSessionMakerMiddleware
from air_bot.bot.middlewares.add_session_maker import AddSessionMakerMiddleware
from air_bot.config import BotConfig
from air_bot.http_session import HttpSessionMaker


class BotService:
    def __init__(
        self,
        config: BotConfig,
        http_session_maker: HttpSessionMaker,
        session_maker: SessionMaker,
    ):
        self.config = config
        self.http_session_maker = http_session_maker
        self.session_maker = session_maker

    async def start(self) -> None:
        self.dp = Dispatcher(storage=MemoryStorage())
        self.bot = Bot(token=self.config.bot_token.get_secret_value())

        self.dp.include_router(start.router)
        self.dp.include_router(add_flight_direction.router)
        self.dp.include_router(user_profile.router)
        # self.dp.include_router(low_prices_calendar.router)

        # scheduler = Scheduler()
        # asyncio.create_task(scheduler.run_loop())

        self.dp.update.middleware(AddSessionMakerMiddleware(self.session_maker))
        self.dp.update.middleware(
            AddHttpSessionMakerMiddleware(self.http_session_maker)
        )
        # await self.ticket_price_checker.start()
        await self.dp.start_polling(self.bot)
