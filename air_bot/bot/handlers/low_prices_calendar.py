import datetime
from datetime import date

from aiogram import Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger

from air_bot.adapters.repo.uow import SqlAlchemyUnitOfWork
from air_bot.adapters.tickets_api import AviasalesTicketsApi
from air_bot.bot.i18n import i18n
from air_bot.bot.keyboards.low_prices_calendar_kb import (
    low_prices_calendar_nav_keyboard,
)
from air_bot.bot.presentation.low_price_calendar import CalendarView
from air_bot.domain.exceptions import TicketsError
from air_bot.domain.model import FlightDirection, Ticket

router = Router()


@router.callback_query(Text(text_startswith="show_low_prices_calendar"))
async def show_low_prices_calendar(
    callback: CallbackQuery,
    state: FSMContext,
    session_maker,
    http_session_maker,
    calendar_view: CalendarView,
) -> None:
    _, direction_id = callback.data.split("|")  # type: ignore[union-attr]
    direction_id = int(direction_id)
    uow = SqlAlchemyUnitOfWork(session_maker)
    async with uow:
        direction_info = await uow.flight_directions.get_direction_info(direction_id)
        await uow.commit()
    if not direction_info:
        await callback.answer(i18n.translate("button_is_outdated"))
        return

    aviasales_api = AviasalesTicketsApi(http_session_maker)
    direction = direction_info.direction
    departure_date = direction.departure_date()
    try:
        tickets_by_date = await aviasales_api.get_cheapest_tickets_for_month(
            direction,
            departure_year=departure_date.year,
            departure_month=departure_date.month,
        )
    except TicketsError as e:
        logger.error(e)
        error_msg = (
            f"{i18n.translate('smth_went_wrong')} {i18n.translate('try_again_later')}"
        )
        await callback.answer(text=error_msg)
        return

    show_prev_button = is_prev_month_allowed(
        direction, departure_date.year, departure_date.month
    )
    show_next_button = is_next_month_allowed(
        direction, departure_date.year, departure_date.month
    )
    calendar_messages = await show_calendar(
        callback.message,  # type: ignore[arg-type]
        calendar_view,
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
    calendar_view: CalendarView,
    month: int,
    tickets_by_date: dict[str, Ticket],
    old_calendar_messages: list[Message],
    show_prev_button: bool,
    show_next_button: bool,
) -> list[Message]:
    calendar_tables = calendar_view.print_calendar(month, tickets_by_date)
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
    callback: CallbackQuery,
    state: FSMContext,
    http_session_maker,
    calendar_view: CalendarView,
) -> None:
    user_data = await state.get_data()
    if "low_prices_calendar_data" not in user_data:
        await callback.answer(text=i18n.translate("button_is_outdated"))
        return
    calendar_data = decrease_month(user_data["low_prices_calendar_data"])
    calendar_messages = await edit_calendar(
        http_session_maker, calendar_view, calendar_data, callback
    )
    calendar_data["calendar_messages"] = calendar_messages
    await state.update_data(low_prices_calendar_data=calendar_data)


@router.callback_query(Text(text="low_prices_calendar__next_month"))
async def show_next_month(
    callback: CallbackQuery,
    state: FSMContext,
    http_session_maker,
    calendar_view: CalendarView,
) -> None:
    user_data = await state.get_data()
    if "low_prices_calendar_data" not in user_data:
        await callback.answer(text=i18n.translate("button_is_outdated"))
        return
    calendar_data = increase_month(user_data["low_prices_calendar_data"])
    calendar_messages = await edit_calendar(
        http_session_maker, calendar_view, calendar_data, callback
    )
    calendar_data["calendar_messages"] = calendar_messages
    await state.update_data(low_prices_calendar_data=calendar_data)


async def edit_calendar(
    http_session_maker,
    calendar_view: CalendarView,
    calendar_data,
    callback: CallbackQuery,
) -> list[Message]:
    """Updates calendar message(s) to ticket prices for departure year and month specified in calendar_data.
    Returns list or updated calendar messages."""
    aviasales_api = AviasalesTicketsApi(http_session_maker)
    try:
        tickets_by_date = await aviasales_api.get_cheapest_tickets_for_month(
            calendar_data["direction"],
            departure_year=calendar_data["year"],
            departure_month=calendar_data["month"],
        )
    except TicketsError as e:
        logger.error(e)
        error_msg = (
            f"{i18n.translate('smth_went_wrong')} {i18n.translate('try_again_later')}"
        )
        await callback.answer(text=error_msg)
        return calendar_data["calendar_messages"]

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
        calendar_view,
        calendar_data["month"],
        tickets_by_date,
        old_calendar_messages,
        show_prev_button,
        show_next_button,
    )
    await callback.answer()
    return calendar_messages


def decrease_month(calendar_data):
    month = calendar_data["month"]
    if month > 1:
        calendar_data["month"] = month - 1
    else:
        calendar_data["month"] = 12
        calendar_data["year"] = calendar_data["year"] - 1
    return calendar_data


def increase_month(calendar_data):
    month = calendar_data["month"]
    if month < 12:
        calendar_data["month"] = month + 1
    else:
        calendar_data["month"] = 1
        calendar_data["year"] = calendar_data["year"] + 1
    return calendar_data


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
