import logging
import typing
from typing import Any

from aiogram import Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from air_bot.aviasales_api.api_layer import AviasalesAPILayer
from air_bot.db.db_manager import DBManager
from air_bot.keyboards.low_prices_calendar_kb import low_prices_calendar_nav_keyboard
from air_bot.utils.low_prices_calendar import print_calendar
from air_bot.utils.db import flight_direction_from_db_type

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(Text(text_startswith="show_low_prices_calendar"))
async def show_low_prices_calendar(
    callback: CallbackQuery,
    state: FSMContext,
    db_manager: DBManager,
    aviasales_api: AviasalesAPILayer,
) -> None:
    _, direction_id = callback.data.split("|")  # type: ignore[union-attr]
    direction_id = int(direction_id)
    user_direction = await db_manager.get_users_flight_direction(
        callback.from_user.id, direction_id
    )
    if not user_direction:
        await callback.answer("Кнопка устарела")
        return

    direction = flight_direction_from_db_type(user_direction)
    departure_date = direction.departure_date()
    tickets_by_date, success = await aviasales_api.get_cheapest_tickets_for_month(
        direction, year=departure_date.year, month=departure_date.month
    )
    if not success:
        await callback.answer(text="Что-то пошло не так. Повторите попытку позже")
        return
    message = await show_calendar(
        callback.message,  # type: ignore[arg-type]
        departure_date.month,
        tickets_by_date,
    )

    await state.clear()
    low_prices_calendar_data = {
        "direction": direction,
        "year": departure_date.year,
        "month": departure_date.month,
        "calendar_message": message,
    }
    await state.update_data(low_prices_calendar_data=low_prices_calendar_data)
    await callback.answer()


async def show_calendar(
    message: Message, month: int, tickets_by_date: dict[str, Any]
) -> None:
    await message.answer(
        print_calendar(month, tickets_by_date),
        reply_markup=low_prices_calendar_nav_keyboard(),
        parse_mode="Markdownv2",
        disable_web_page_preview=True,
    )


@router.callback_query(Text(text="low_prices_calendar__prev_month"))
async def show_previous_month(
    callback: CallbackQuery, state: FSMContext, aviasales_api: AviasalesAPILayer
) -> None:
    user_data = await state.get_data()
    if "low_prices_calendar_data" not in user_data:
        await callback.answer(text="Кнопка устарела")
        return
    calendar_data = decrease_month(user_data["low_prices_calendar_data"])
    await edit_calendar(aviasales_api, calendar_data, callback)


async def edit_calendar(aviasales_api, calendar_data, callback):
    tickets_by_date, success = await aviasales_api.get_cheapest_tickets_for_month(
        calendar_data["direction"], calendar_data["year"], calendar_data["month"]
    )
    if not success:
        await callback.answer(text="Что-то пошло не так. Повторите попытку позже")
        return
    message = calendar_data["calendar_message"]
    await message.edit_text(
        print_calendar(calendar_data["month"], tickets_by_date),
        reply_markup=low_prices_calendar_nav_keyboard(),
        parse_mode="Markdownv2",
        disable_web_page_preview=True,
    )
    await callback.answer()


@router.callback_query(Text(text="low_prices_calendar__next_month"))
async def show_next_month(
    callback: CallbackQuery, state: FSMContext, aviasales_api: AviasalesAPILayer
) -> None:
    user_data = await state.get_data()
    if "low_prices_calendar_data" not in user_data:
        await callback.answer(text="Кнопка устарела")
        return
    calendar_data = increase_month(user_data["low_prices_calendar_data"])
    await edit_calendar(aviasales_api, calendar_data, callback)


def decrease_month(low_prices_calendar_data) -> dict[str, typing.Any]:
    month = low_prices_calendar_data["month"]
    if month > 1:
        low_prices_calendar_data["month"] = month - 1
    else:
        low_prices_calendar_data["month"] = 12
        low_prices_calendar_data["year"] = low_prices_calendar_data["year"] - 1
    return low_prices_calendar_data


def increase_month(low_prices_calendar_data) -> dict[str, typing.Any]:
    month = low_prices_calendar_data["month"]
    if month < 12:
        low_prices_calendar_data["month"] = month + 1
    else:
        low_prices_calendar_data["month"] = 1
        low_prices_calendar_data["year"] = low_prices_calendar_data["year"] + 1
    return low_prices_calendar_data
