import asyncio

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from air_bot.bot.handlers import start, add_flight_direction
from air_bot.bot.i18n import Translator
from air_bot.bot.middlewares.add_translator_middleware import AddTranslatorMiddleware
from air_bot.config import BotConfig


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

        translator = Translator(locale="en")
        self.dp.update.middleware(AddTranslatorMiddleware(translator))
        # scheduler = Scheduler()
        # asyncio.create_task(scheduler.run_loop())

        # self.dp.update.middleware(AddDBManager(db_manager))

        # aviasales_api = AviasalesAPILayer(aiohttp_session, config.aviasales_api_token)
        # self.dp.update.middleware(AddAviasalesAPILayerMiddleware(aviasales_api))
        # self.ticket_price_checker = TicketPriceChecker(
        #     self.bot,
        #     aviasales_api,
        #     db_manager,
        #     scheduler,
        #     config.ticket_price_checker_settings,
        # )
        # self.dp.update.middleware(AddTicketPriceChecker(self.ticket_price_checker))

    def start(self) -> None:
        # await self.ticket_price_checker.start()
        asyncio.create_task(self.dp.start_polling(self.bot))
