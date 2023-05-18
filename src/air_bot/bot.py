import asyncio
import logging

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import air_bot.db as db
from air_bot.aiohttp_logging import get_trace_config
from air_bot.checker.ticket_price_checker import TicketPriceChecker
from air_bot.config import config
from air_bot.handlers import start, add_flight_direction, user_profile, low_prices_calendar
from air_bot.middlewares.add_aviasales_api_layer import AddAviasalesAPILayerMiddleware
from air_bot.middlewares.add_db import AddDb
from air_bot.middlewares.add_ticket_price_checker import AddTicketPriceChecker
from air_bot.scheduler import Scheduler
from air_bot.aviasales_api.api_layer import AviasalesAPILayer

logger = logging.getLogger("AirBot")


async def main() -> None:
    logger.setLevel(logging.INFO)
    setup_console_logger(logger)
    setup_file_logger(logger)

    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(token=config.bot_token.get_secret_value())

    dp.include_router(start.router)
    dp.include_router(add_flight_direction.router)
    dp.include_router(user_profile.router)
    dp.include_router(low_prices_calendar.router)

    scheduler = Scheduler()
    asyncio.create_task(scheduler.run_loop())

    try:
        DB = db.DB(config)
    except Exception as ex:
        logger.exception(ex)
        return
    dp.update.middleware(AddDb(DB))
    async with aiohttp.ClientSession(trace_configs=[get_trace_config()]) as session:
        aviasales_api = AviasalesAPILayer(session, config.aviasales_api_token)
        dp.update.middleware(AddAviasalesAPILayerMiddleware(aviasales_api))
        ticket_price_checker = TicketPriceChecker(
            bot, aviasales_api, DB, scheduler, config.ticket_price_checker_settings
        )
        dp.update.middleware(AddTicketPriceChecker(ticket_price_checker))
        await dp.start_polling(bot)


def cli() -> None:
    """Wrapper for command line"""
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")


def setup_console_logger(lgr: logging.Logger) -> None:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    ch.setFormatter(ch_formatter)
    lgr.addHandler(ch)


def setup_file_logger(lgr: logging.Logger) -> None:
    ch = logging.FileHandler("AirBot.log", encoding="utf-8")
    ch.setLevel(logging.INFO)
    ch_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    ch.setFormatter(ch_formatter)
    logger.addHandler(ch)


if __name__ == "__main__":
    cli()
