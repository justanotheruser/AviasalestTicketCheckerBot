import datetime
import logging
import typing
from datetime import date
from typing import Any

from aiogram import Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from air_bot.aviasales_api.api_layer import AviasalesAPILayer
from air_bot.bot_types import FlightDirection
from air_bot.db.db_manager import DBManager
from air_bot.keyboards.low_prices_calendar_kb import low_prices_calendar_nav_keyboard
from air_bot.utils.db import flight_direction_from_db_type
from air_bot.utils.low_prices_calendar import print_calendar

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
        direction,
        departure_year=departure_date.year,
        departure_month=departure_date.month,
    )
    if not success:
        await callback.answer(text="Что-то пошло не так. Повторите попытку позже")
        return

    show_prev_button = is_prev_month_allowed(
        direction, departure_date.year, departure_date.month
    )
    show_next_button = is_next_month_allowed(
        direction, departure_date.year, departure_date.month
    )
    calendar_messages = await show_calendar(
        callback.message,  # type: ignore[arg-type]
        departure_date.month,
        tickets_by_date,
        [],
        show_prev_button,
        show_next_button,
    )

    await state.clear()
    low_prices_calendar_data = {
        "direction": direction,
        "year": departure_date.year,
        "month": departure_date.month,
        "calendar_messages": calendar_messages,
    }
    await state.update_data(low_prices_calendar_data=low_prices_calendar_data)
    await callback.answer()


async def show_calendar(
    message_for_answering: Message,
    month: int,
    tickets_by_date: dict[str, Any],
    old_calendar_messages: list[Message],
    show_prev_button: bool,
    show_next_button: bool,
) -> list[Message]:
    calendar_tables = print_calendar(month, tickets_by_date)
    updated_calendar_messages = []
    for i, (message, table) in enumerate(zip(old_calendar_messages, calendar_tables)):
        if i < len(calendar_tables) - 1:
            await message.edit_text(
                table,
                parse_mode="Markdownv2",
                disable_web_page_preview=True,
            )
        else:
            await message.edit_text(
                table,
                reply_markup=low_prices_calendar_nav_keyboard(
                    show_prev_button, show_next_button
                ),
                parse_mode="Markdownv2",
                disable_web_page_preview=True,
            )
        updated_calendar_messages.append(message)

    n_new_messages = len(calendar_tables) - len(old_calendar_messages)
    for i in range(n_new_messages):
        if i < n_new_messages - 1:
            message = await message_for_answering.answer(
                calendar_tables[len(old_calendar_messages) + i],
                parse_mode="Markdownv2",
                disable_web_page_preview=True,
            )
        else:
            message = await message_for_answering.answer(
                calendar_tables[len(old_calendar_messages) + i],
                reply_markup=low_prices_calendar_nav_keyboard(
                    show_prev_button, show_next_button
                ),
                parse_mode="Markdownv2",
                disable_web_page_preview=True,
            )
        updated_calendar_messages.append(message)

    n_tables = len(calendar_tables)
    if len(old_calendar_messages) > n_tables:
        for excess_message in old_calendar_messages[n_tables:]:
            await excess_message.delete()

    return updated_calendar_messages


@router.callback_query(Text(text="low_prices_calendar__prev_month"))
async def show_previous_month(
    callback: CallbackQuery, state: FSMContext, aviasales_api: AviasalesAPILayer
) -> None:
    user_data = await state.get_data()
    if "low_prices_calendar_data" not in user_data:
        await callback.answer(text="Кнопка устарела")
        return
    calendar_data = decrease_month(user_data["low_prices_calendar_data"])
    calendar_messages = await edit_calendar(aviasales_api, calendar_data, callback)
    calendar_data["calendar_messages"] = calendar_messages
    await state.update_data(low_prices_calendar_data=calendar_data)


@router.callback_query(Text(text="low_prices_calendar__next_month"))
async def show_next_month(
    callback: CallbackQuery, state: FSMContext, aviasales_api: AviasalesAPILayer
) -> None:
    user_data = await state.get_data()
    if "low_prices_calendar_data" not in user_data:
        await callback.answer(text="Кнопка устарела")
        return
    calendar_data = increase_month(user_data["low_prices_calendar_data"])
    calendar_messages = await edit_calendar(aviasales_api, calendar_data, callback)
    calendar_data["calendar_messages"] = calendar_messages
    await state.update_data(low_prices_calendar_data=calendar_data)


async def edit_calendar(aviasales_api, calendar_data, callback):
    tickets_by_date, success = await aviasales_api.get_cheapest_tickets_for_month(
        calendar_data["direction"], calendar_data["year"], calendar_data["month"]
    )
    if not success:
        await callback.answer(text="Что-то пошло не так. Повторите попытку позже")
        return
    old_calendar_messages = calendar_data["calendar_messages"]
    calendar_date = date(
        year=calendar_data["year"], month=calendar_data["month"], day=1
    )
    show_next_button = is_next_month_allowed(
        calendar_data["direction"], calendar_date.year, calendar_date.month
    )
    show_prev_button = is_prev_month_allowed(
        calendar_data["direction"], calendar_date.year, calendar_date.month
    )
    calendar_messages = await show_calendar(
        callback.message,  # type: ignore[arg-type]
        calendar_data["month"],
        tickets_by_date,
        old_calendar_messages,
        show_prev_button,
        show_next_button,
    )
    await callback.answer()
    return calendar_messages


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


def is_next_month_allowed(
    direction: FlightDirection, departure_year: int, departure_month: int
) -> bool:
    if return_date := direction.return_date():
        if return_date.year < departure_year:
            return False  # Can't return before departure date
        if return_date.month <= departure_month:
            return False  # Can't return before departure date
    return True


def is_prev_month_allowed(
    direction: FlightDirection, departure_year: int, departure_month: int
) -> bool:
    now = datetime.datetime.now()
    if now.year == departure_year and now.month == departure_month:
        return False
    # Time span of more than 30 days not supported by Aviasales API
    if return_date := direction.return_date():
        if return_date.year > departure_year and departure_month < 12:
            return False
        elif return_date.month - departure_month > 0:
            return False
    return True
