import asyncio
import logging

from aiogram import Router, F
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

# from air_bot.bot.keyboards.add_flight_direction_kb import (
#     with_or_without_return_keyboard,
#     with_or_without_transfer_keyboard,
#     choose_airport_keyboard,
#     choose_month_keyboard,
# )
from air_bot.bot.keyboards.user_home_kb import user_home_keyboard
# from air_bot.bot.keyboards.low_prices_calendar_kb import show_low_prices_calendar_keyboard
# from air_bot.bot.utils.date import DateReader
# from air_bot.bot.utils.tickets import print_tickets

logger = logging.getLogger(__name__)

router = Router()


class NewDirection(StatesGroup):
    choosing_with_return_or_not = State()
    choosing_with_transfer_or_not = State()
    choosing_airport_start = State()
    choosing_specific_airport_start = State()
    choosing_airport_end = State()
    choosing_specific_airport_end = State()
    choosing_departure_date = State()
    choosing_return_date = State()


@router.callback_query(Text(text="add_flight_direction"))
async def add_flight_direction_inline(
    callback: CallbackQuery, state: FSMContext
) -> None:
    await add_flight_direction(callback.message, state)
    await callback.answer()


@router.message(Command(commands=["cancel"]))
@router.message(Text(text="отмена", text_ignore_case=True))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await message.answer(
        text="Добавление маршрута отменено", reply_markup=user_home_keyboard()
    )
    await state.clear()


@router.message(Text(text="🔍 новый поиск"))
@router.message(Text(text="/новый поиск"))
@router.message(Command(commands=["search", "новый поиск"]))
async def add_flight_direction(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Выберите тип поиска 👇", reply_markup=with_or_without_return_keyboard()
    )
    await state.clear()
    await state.set_state(NewDirection.choosing_with_return_or_not)