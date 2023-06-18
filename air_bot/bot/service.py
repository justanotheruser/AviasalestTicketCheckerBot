import asyncio

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from air_bot.adapters.locations_api import TravelPayoutsLocationsApi
from air_bot.bot.handlers import add_flight_direction, start
from air_bot.bot.middlewares.add_locations_api import AddLocationsApiMiddleware
from air_bot.bot.middlewares.add_tickets_service import AddTicketsServiceMiddleware
from air_bot.config import BotConfig
from air_bot.service_layer.tickets_service import TicketsService


class BotService:
    def __init__(
        self,
        config: BotConfig,
        # db_manager: DBManager,
        aiohttp_session: aiohttp.ClientSession,
    ):
        self.dp = Dispatcher(storage=MemoryStorage())
        self.bot = Bot(token=config.bot_token.get_secret_value())

        self.dp.include_router(start.router)
        self.dp.include_router(add_flight_direction.router)
        # self.dp.include_router(user_profile.router)
        # self.dp.include_router(low_prices_calendar.router)

        # scheduler = Scheduler()
        # asyncio.create_task(scheduler.run_loop())

        # self.dp.update.middleware(AddDBManager(db_manager))

        locations_api = TravelPayoutsLocationsApi(aiohttp_session, config.locale)
        self.dp.update.middleware(AddLocationsApiMiddleware(locations_api))
        tickets_service = TicketsService(None, None, None, None)
        self.dp.update.middleware(AddTicketsServiceMiddleware(tickets_service))

    def start(self) -> None:
        # await self.ticket_price_checker.start()
        asyncio.create_task(self.dp.start_polling(self.bot))
