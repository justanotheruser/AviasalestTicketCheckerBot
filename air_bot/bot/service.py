import asyncio

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from air_bot.adapters.locations_api import TravelPayoutsLocationsApi
from air_bot.adapters.repo.session_maker import SessionMaker
from air_bot.bot.handlers import add_flight_direction, start, user_profile
from air_bot.bot.middlewares.add_locations_api import AddLocationsApiMiddleware
from air_bot.bot.middlewares.add_session_maker import AddSessionMakerMiddleware
from air_bot.config import BotConfig


class BotService:
    def __init__(
        self,
        config: BotConfig,
        aiohttp_session: aiohttp.ClientSession,
        session_maker: SessionMaker,
    ):
        self.dp = Dispatcher(storage=MemoryStorage())
        self.bot = Bot(token=config.bot_token.get_secret_value())

        self.dp.include_router(start.router)
        self.dp.include_router(add_flight_direction.router)
        self.dp.include_router(user_profile.router)
        # self.dp.include_router(low_prices_calendar.router)

        # scheduler = Scheduler()
        # asyncio.create_task(scheduler.run_loop())

        self.dp.update.middleware(AddSessionMakerMiddleware(session_maker))
        locations_api = TravelPayoutsLocationsApi(aiohttp_session, config.locale)
        self.dp.update.middleware(AddLocationsApiMiddleware(locations_api))

    def start(self) -> None:
        # await self.ticket_price_checker.start()
        asyncio.create_task(self.dp.start_polling(self.bot))
