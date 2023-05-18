import asyncio
import logging

from aiogram import Router, F
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from async_timeout import timeout

from air_bot.aviasales_api.api_layer import AviasalesAPILayer
from air_bot.bot_types import FlightDirection
from air_bot.checker.ticket_price_checker import TicketPriceChecker
from air_bot.db import DB
from air_bot.keyboards.add_flight_direction_kb import (
    with_or_without_return_keyboard,
    with_or_without_transfer_keyboard,
    choose_airport_keyboard,
    choose_month_keyboard,
)
from air_bot.keyboards.user_home_kb import user_home_keyboard
from air_bot.utils.date import DateReader
from air_bot.utils.tickets import print_tickets

logger = logging.getLogger("AirBot")

router = Router()
