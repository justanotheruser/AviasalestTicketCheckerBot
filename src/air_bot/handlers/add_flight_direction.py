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
from air_bot.db.db_manager import DBManager
from air_bot.keyboards.add_flight_direction_kb import (
    with_or_without_return_keyboard,
    with_or_without_transfer_keyboard,
    choose_airport_keyboard,
    choose_month_keyboard,
)
from air_bot.keyboards.user_home_kb import user_home_keyboard
from air_bot.keyboards.low_prices_calendar_kb import show_low_prices_calendar_keyboard
from air_bot.utils.date import DateReader
from air_bot.utils.tickets import print_tickets

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


@router.callback_query(
    NewDirection.choosing_with_return_or_not,
    F.data.in_(["with_return", "without_return"]),
)
async def choose_with_or_without_transfer(
    callback: CallbackQuery, state: FSMContext
) -> None:
    await state.update_data(with_return=callback.data == "with_return")
    await callback.message.answer(  # type: ignore[union-attr]
        "Прямые рейсы 👇",
        reply_markup=with_or_without_transfer_keyboard(),
    )
    await state.set_state(NewDirection.choosing_with_transfer_or_not)
    await callback.answer()


@router.callback_query(
    NewDirection.choosing_with_transfer_or_not,
    F.data.in_(["with_transfer", "without_transfer"]),
)
async def choose_airport_start(callback: CallbackQuery, state: FSMContext) -> None:
    with_transfer = callback.data == "with_transfer"
    await state.update_data(with_transfer=with_transfer)
    await callback.message.answer("🛫 Укажите пункт отправления: ")  # type: ignore[union-attr]
    await callback.answer()
    await state.set_state(NewDirection.choosing_airport_start)


@router.message(NewDirection.choosing_airport_start, F.text)
async def choose_specific_airport_start(
    message: Message, state: FSMContext, aviasales_api: AviasalesAPILayer
) -> None:
    try:
        # TODO: move timeout inside AviasalesAPILayer
        async with timeout(10):
            text: str = message.text  # type: ignore[assignment]
            locations = await aviasales_api.get_locations(text)
    except asyncio.TimeoutError:
        await message.answer("Что-то пошло не так. 😔 \nПопробуйте еще раз. 🔄")
        return
    if not locations:
        await message.answer("Такого пункта нет. 😔 \nПопробуйте еще раз. 🔄")
    elif len(locations) == 1:
        await state.update_data(
            start_code=locations[0].code, start_name=locations[0].name
        )
        await message.answer("🛬 Укажите пункт прибытия: ")
        await state.set_state(NewDirection.choosing_airport_end)
    else:
        await message.answer(
            "Уточните, что именно нужно: 👇",
            reply_markup=choose_airport_keyboard(locations),
        )
        await state.set_state(NewDirection.choosing_specific_airport_start)


@router.callback_query(NewDirection.choosing_specific_airport_start)
async def choose_airport_end(callback: CallbackQuery, state: FSMContext) -> None:
    start_name, start_code = callback.data.split("|")  # type: ignore[union-attr]
    await state.update_data(start_code=start_code, start_name=start_name)
    await callback.message.answer("🛬 Укажите пункт прибытия: ")  # type: ignore[union-attr]
    await callback.answer()
    await state.set_state(NewDirection.choosing_airport_end)


@router.message(NewDirection.choosing_airport_end, F.text)
async def choose_specific_airport_end(
    message: Message, state: FSMContext, aviasales_api: AviasalesAPILayer
) -> None:
    try:
        async with timeout(10):
            text: str = message.text  # type: ignore[assignment]
            locations = await aviasales_api.get_locations(text)
    except asyncio.TimeoutError:
        await message.answer("Что-то пошло не так. 😔 \nПопробуйте еще раз. 🔄")
        return
    if not locations:
        await message.answer("Такого пункта нет. 😔 \nПопробуйте еще раз. 🔄")
    elif len(locations) == 1:
        await state.update_data(end_code=locations[0].code, end_name=locations[0].name)
        await ask_for_departure_date(message, state)
    else:
        await message.answer(
            "Уточните, что именно нужно: 👇",
            reply_markup=choose_airport_keyboard(locations),
        )
        await state.set_state(NewDirection.choosing_specific_airport_end)


@router.callback_query(NewDirection.choosing_specific_airport_end)
async def choose_departure_date(callback: CallbackQuery, state: FSMContext) -> None:
    end_name, end_code = callback.data.split("|")  # type: ignore[union-attr]
    await state.update_data(end_code=end_code, end_name=end_name)
    await ask_for_departure_date(callback.message, state)  # type: ignore[arg-type]
    await callback.answer()


async def ask_for_departure_date(message: Message, state: FSMContext) -> None:
    date_examples = ", ".join(f'"{example}"' for example in DateReader().get_examples())
    await message.answer(
        "📅 Укажите дату отправления:\n"
        "можно выбрать целый месяц или прислать мне дату, например:\n"
        f"{date_examples}",
        reply_markup=choose_month_keyboard(),
    )
    await state.set_state(NewDirection.choosing_departure_date)


@router.message(NewDirection.choosing_departure_date, F.text)
async def got_departure_date_as_text(
    message: Message,
    state: FSMContext,
    aviasales_api: AviasalesAPILayer,
    db_manager: DBManager,
    ticket_price_checker: TicketPriceChecker,
) -> None:
    departure_date = DateReader().read_date(message.text)  # type: ignore[arg-type]
    if not departure_date:
        await message.answer(
            text="Не удалось распознать дату, попробуйте указать еще раз. 🔄"
        )
        return
    await got_departure_date(
        departure_date,
        message.from_user.id,  # type: ignore[union-attr]
        message,
        state,
        aviasales_api,
        db_manager,
        ticket_price_checker,
    )


@router.callback_query(NewDirection.choosing_departure_date)
async def got_departure_date_from_button(
    callback: CallbackQuery,
    state: FSMContext,
    aviasales_api: AviasalesAPILayer,
    db_manager: DBManager,
    ticket_price_checker: TicketPriceChecker,
) -> None:
    departure_date: str = callback.data  # type: ignore[assignment]
    await got_departure_date(
        departure_date,
        callback.from_user.id,
        callback.message,  # type: ignore[arg-type]
        state,
        aviasales_api,
        db_manager,
        ticket_price_checker,
    )
    await callback.answer()


async def got_departure_date(
    departure_date: str,
    user_id: int,
    message: Message,
    state: FSMContext,
    aviasales_api: AviasalesAPILayer,
    db_manager: DBManager,
    ticket_price_checker: TicketPriceChecker,
) -> None:
    await state.update_data(departure_date=departure_date)
    user_data = await state.get_data()
    if user_data["with_return"]:
        await ask_for_return_date(message, state)
    else:
        await show_tickets(
            message, user_id, aviasales_api, state, db_manager, ticket_price_checker
        )


async def ask_for_return_date(message: Message, state: FSMContext) -> None:
    date_examples = ", ".join(DateReader().get_examples())
    await message.answer(
        "📅 Укажите дату возвращения:\n"
        "Выберите месяц или введите дату.\n"
        f"Например: {date_examples}",
        reply_markup=choose_month_keyboard(),
    )
    await state.set_state(NewDirection.choosing_return_date)


@router.message(NewDirection.choosing_return_date, F.text)
async def got_return_date_as_text(
    message: Message,
    aviasales_api: AviasalesAPILayer,
    state: FSMContext,
    db_manager: DBManager,
    ticket_price_checker: TicketPriceChecker,
) -> None:
    return_date = DateReader().read_date(message.text)  # type: ignore[arg-type]
    if not return_date:
        await message.answer(
            text="Не удалось распознать дату, попробуйте указать еще раз. 🔄"
        )
        return
    await state.update_data(return_date=return_date)
    await show_tickets(
        message,
        message.from_user.id,  # type: ignore[union-attr]
        aviasales_api,
        state,
        db_manager,
        ticket_price_checker,
    )


@router.callback_query(NewDirection.choosing_return_date)
async def got_return_date_from_button(
    callback: CallbackQuery,
    aviasales_api: AviasalesAPILayer,
    state: FSMContext,
    db_manager: DBManager,
    ticket_price_checker: TicketPriceChecker,
) -> None:
    return_date: str = callback.data  # type: ignore[assignment]
    await state.update_data(return_date=return_date)
    await show_tickets(
        callback.message,  # type: ignore[arg-type]
        callback.from_user.id,
        aviasales_api,
        state,
        db_manager,
        ticket_price_checker,
    )
    await callback.answer()


async def show_tickets(
    message: Message,
    user_id: int,
    aviasales_api: AviasalesAPILayer,
    state: FSMContext,
    db_manager: DBManager,
    ticket_price_checker: TicketPriceChecker,
) -> None:
    user_data = await state.get_data()
    return_date = user_data.get("return_date", None)
    direction = FlightDirection(
        start_code=user_data["start_code"],
        start_name=user_data["start_name"],
        end_code=user_data["end_code"],
        end_name=user_data["end_name"],
        with_transfer=user_data["with_transfer"],
        departure_at=user_data["departure_date"],
        return_at=return_date,
    )
    # TODO: move timeout inside AviasalesAPILayer
    try:
        async with timeout(10):
            tickets = await aviasales_api.get_tickets(direction)
    except Exception as e:
        logger.exception(e)
        await message.answer(
            "Что-то пошло не так. 😔 \nПопробуйте задать поиск заного. 🔄",
            reply_markup=user_home_keyboard(),
        )
        await state.clear()
        return

    ticket_price_checker.schedule_check(user_id, direction)
    cheapest_price = tickets[0]["price"] if tickets else None
    direction_id = await db_manager.save_or_update_flight_direction(
        user_id=user_id, direction=direction, price=cheapest_price
    )
    if not direction_id:
        await message.answer(
            "Что-то пошло не так. 😔 \nПопробуйте задать поиск заного. 🔄",
            reply_markup=user_home_keyboard(),
        )
        await state.clear()
        return

    await message.answer(
        text="✅ Направление добавлено, а вот самые низкие цены на сегодня\n👇👇👇"
    )
    await message.answer(
        text=print_tickets(tickets, direction),
        parse_mode="html",
        disable_web_page_preview=True,
        reply_markup=show_low_prices_calendar_keyboard(direction_id),
    )
    await state.clear()
