from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger

from air_bot.adapters.locations_api import TravelPayoutsLocationsApi
from air_bot.adapters.repo.uow import SqlAlchemyUnitOfWork
from air_bot.adapters.tickets_api import AviasalesTicketsApi
from air_bot.bot.i18n import i18n
from air_bot.bot.keyboards.choose_location_kb import choose_location_keyboard
from air_bot.bot.keyboards.choose_month_kb import choose_month_kb
from air_bot.bot.keyboards.direct_or_transfer_kb import direct_or_transfer_kb
from air_bot.bot.keyboards.low_prices_calendar_kb import (
    show_low_prices_calendar_keyboard,
)
from air_bot.bot.keyboards.user_home_kb import user_home_kb
from air_bot.bot.keyboards.with_or_without_return_kb import with_or_without_return_kb
from air_bot.bot.presentation.tickets import TicketView
from air_bot.bot.utils.date import date_reader
from air_bot.bot.utils.validation import validate_user_data_for_direction
from air_bot.config import config
from air_bot.domain.exceptions import (
    DuplicatedFlightDirection,
    TicketsAPIConnectionError,
)
from air_bot.domain.model import FlightDirection
from air_bot.service.user import check_if_new_tracking_available, track
from air_bot.settings import SettingsStorage

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


@router.callback_query(lambda c: c.data == "add_flight_direction")
async def add_flight_direction_inline(
    callback: CallbackQuery,
    state: FSMContext,
    session_maker,
    settings_storage: SettingsStorage,
) -> None:
    await add_flight_direction(
        callback.message, state, session_maker, settings_storage, callback.from_user.id
    )
    await callback.answer()


@router.message(Command(commands=["cancel"], ignore_case=True))
@router.message(F.text.lower() == i18n.translate("cancel").lower())
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await message.answer(
        text="Добавление маршрута отменено", reply_markup=user_home_kb.keyboard
    )
    await state.clear()


@router.message(F.text == user_home_kb.new_search_btn_text)
@router.message(Command(commands=["search"]))
async def add_flight_direction(
    message: Message,
    state: FSMContext,
    session_maker,
    settings_storage: SettingsStorage,
    user_id=None,
):
    if user_id is None:
        # This is so we get correct user id for both usual and inline buttons
        user_id = message.from_user.id  # type: ignore[union-attr]
    uow = SqlAlchemyUnitOfWork(session_maker)
    if not await check_if_new_tracking_available(settings_storage, uow, user_id):
        await message.answer(text=i18n.translate("you_reached_tracking_limit"))
        return
    await message.answer(
        f'{i18n.translate("choose_search_type")} 👇',
        reply_markup=with_or_without_return_kb.keyboard,
    )
    await state.clear()
    await state.set_state(NewDirection.choosing_with_return_or_not)


@router.callback_query(
    NewDirection.choosing_with_return_or_not,
    lambda c: c.data
    in [
        with_or_without_return_kb.one_way_cb_data,
        with_or_without_return_kb.round_trip_cb_data,
    ],
)
async def choose_with_or_without_transfer(
    callback: CallbackQuery, state: FSMContext
) -> None:
    with_return = callback.data == with_or_without_return_kb.round_trip_cb_data
    await state.update_data(with_return=with_return)
    await callback.message.answer(  # type: ignore[union-attr]
        f"{i18n.translate('choose_direct_or_transfer')} 👇",
        reply_markup=direct_or_transfer_kb.keyboard,
    )
    await state.set_state(NewDirection.choosing_with_transfer_or_not)
    await callback.answer()


@router.callback_query(
    NewDirection.choosing_with_transfer_or_not,
    lambda c: c.data
    in [
        direct_or_transfer_kb.direct_flights_cb_data,
        direct_or_transfer_kb.transfer_flights_cb_data,
    ],
)
async def choose_airport_start(callback: CallbackQuery, state: FSMContext) -> None:
    with_transfer = callback.data == direct_or_transfer_kb.transfer_flights_cb_data
    await state.update_data(with_transfer=with_transfer)
    await callback.message.answer(f"🛫 {i18n.translate('choose_departure_point')}: ")  # type: ignore[union-attr]
    await callback.answer()
    await state.set_state(NewDirection.choosing_airport_start)


@router.message(NewDirection.choosing_airport_start, F.text)
async def choose_specific_airport_start(
    message: Message, state: FSMContext, http_session_maker
) -> None:
    locations_api = TravelPayoutsLocationsApi(http_session_maker, config.locale)
    try:
        text: str = message.text  # type: ignore[assignment]
        locations = await locations_api.get_locations(text)
    except Exception as e:
        logger.error(e)
        response = (
            f"{i18n.translate('smth_went_wrong')} 😔 \n"
            f"{i18n.translate('try_again')} 🔄"
        )
        await message.answer(response)
        return
    if not locations:
        response = (
            f"{i18n.translate('no_such_location')} 😔 \n"
            f"{i18n.translate('try_again')} 🔄"
        )
        await message.answer(response)
        return
    if len(locations) == 1:
        await state.update_data(
            start_code=locations[0].code, start_name=locations[0].name
        )
        await message.answer(f"🛬 {i18n.translate('choose_arrival_point')}: ")
        await state.set_state(NewDirection.choosing_airport_end)
    else:
        await message.answer(
            f"{i18n.translate('specify_exact_location')}: 👇",
            reply_markup=choose_location_keyboard(locations),
        )
        await state.set_state(NewDirection.choosing_specific_airport_start)


@router.callback_query(NewDirection.choosing_specific_airport_start)
async def choose_airport_end(callback: CallbackQuery, state: FSMContext) -> None:
    start_name, start_code = callback.data.split("|")  # type: ignore[union-attr]
    await state.update_data(start_code=start_code, start_name=start_name)
    await callback.message.answer(f"🛬 {i18n.translate('choose_arrival_point')}: ")  # type: ignore[union-attr]
    await callback.answer()
    await state.set_state(NewDirection.choosing_airport_end)


@router.message(NewDirection.choosing_airport_end, F.text)
async def choose_specific_airport_end(
    message: Message, state: FSMContext, http_session_maker
) -> None:
    locations_api = TravelPayoutsLocationsApi(http_session_maker, config.locale)
    try:
        text: str = message.text  # type: ignore[assignment]
        locations = await locations_api.get_locations(text)
    except Exception:
        response = (
            f"{i18n.translate('smth_went_wrong')} 😔 \n"
            f"{i18n.translate('try_again')} 🔄"
        )
        await message.answer(response)
        return
    if not locations:
        response = (
            f"{i18n.translate('no_such_location')} 😔 \n"
            f"{i18n.translate('try_again')} 🔄"
        )
        await message.answer(response)
        return
    elif len(locations) == 1:
        end_code = locations[0].code
        await state.update_data(end_code=end_code, end_name=locations[0].name)
        await ask_for_departure_date(message, state)
    else:
        await message.answer(
            f"{i18n.translate('specify_exact_location')}: 👇",
            reply_markup=choose_location_keyboard(locations),
        )
        await state.set_state(NewDirection.choosing_specific_airport_end)


@router.callback_query(NewDirection.choosing_specific_airport_end)
async def choose_departure_date(callback: CallbackQuery, state: FSMContext) -> None:
    end_name, end_code = callback.data.split("|")  # type: ignore[union-attr]
    await state.update_data(end_code=end_code, end_name=end_name)
    await ask_for_departure_date(callback.message, state)  # type: ignore[arg-type]
    await callback.answer()


async def ask_for_departure_date(message: Message, state: FSMContext) -> None:
    date_examples = ", ".join(f'"{example}"' for example in date_reader.get_examples())
    await message.answer(
        f"📅 {i18n.translate('choose_departure_date')}:\n"
        f"{i18n.translate('choose_month_or_specific_date')}:\n{date_examples}",
        reply_markup=choose_month_kb.keyboard(),
    )
    await state.set_state(NewDirection.choosing_departure_date)


@router.message(NewDirection.choosing_departure_date, F.text)
async def got_departure_date_as_text(
    message: Message,
    state: FSMContext,
    session_maker,
    http_session_maker,
    ticket_view: TicketView,
):
    departure_date = date_reader.read_date(message.text)  # type: ignore[arg-type]
    if not departure_date:
        await message.answer(
            text=f"{i18n.translate('cant_recognize_date_try_again')}. 🔄"
        )
        return
    await got_departure_date(
        departure_date,
        message.from_user.id,  # type: ignore[union-attr]
        message,
        state,
        session_maker,
        http_session_maker,
        ticket_view,
    )


@router.callback_query(NewDirection.choosing_departure_date)
async def got_departure_date_from_button(
    callback: CallbackQuery,
    state: FSMContext,
    session_maker,
    http_session_maker,
    ticket_view: TicketView,
) -> None:
    departure_date: str = callback.data  # type: ignore[assignment]
    await got_departure_date(
        departure_date,
        callback.from_user.id,
        callback.message,  # type: ignore[arg-type]
        state,
        session_maker,
        http_session_maker,
        ticket_view,
    )
    await callback.answer()


async def got_departure_date(
    departure_date: str,
    user_id: int,
    message: Message,
    state: FSMContext,
    session_maker,
    http_session_maker,
    ticket_view: TicketView,
) -> None:
    await state.update_data(departure_at=departure_date)
    user_data = await state.get_data()
    if user_data["with_return"]:
        await ask_for_return_date(message, state)
        return
    await add_direction_and_show_result(
        user_id, state, message, session_maker, http_session_maker, ticket_view
    )


async def ask_for_return_date(message: Message, state: FSMContext) -> None:
    date_examples = ", ".join(date_reader.get_examples())
    await message.answer(
        f"📅 {i18n.translate('choose_arrival_date')}:\n"
        f"{i18n.translate('choose_month_or_specific_date')}:\n{date_examples}",
        reply_markup=choose_month_kb.keyboard(),
    )
    await state.set_state(NewDirection.choosing_return_date)


@router.message(NewDirection.choosing_return_date, F.text)
async def got_return_date_as_text(
    message: Message,
    state: FSMContext,
    session_maker,
    http_session_maker,
    ticket_view: TicketView,
):
    return_date = date_reader.read_date(message.text)  # type: ignore[arg-type]
    if not return_date:
        await message.answer(
            text=f"{i18n.translate('cant_recognize_date_try_again')}. 🔄"
        )
        return
    await state.update_data(return_at=return_date)
    await add_direction_and_show_result(
        message.from_user.id,  # type: ignore[union-attr]
        state,
        message,
        session_maker,
        http_session_maker,
        ticket_view,
    )


@router.callback_query(NewDirection.choosing_return_date)
async def got_return_date_from_button(
    callback: CallbackQuery,
    state: FSMContext,
    session_maker,
    http_session_maker,
    ticket_view: TicketView,
):
    return_date: str = callback.data  # type: ignore[assignment]
    await state.update_data(return_at=return_date)
    await add_direction_and_show_result(
        callback.from_user.id,
        state,
        callback.message,  # type: ignore[arg-type]
        session_maker,
        http_session_maker,
        ticket_view,
    )
    await callback.answer()


async def add_direction_and_show_result(
    user_id: int,
    state: FSMContext,
    message: Message,
    session_maker,
    http_session_maker,
    ticket_view: TicketView,
):
    user_data = await state.get_data()
    if not validate_user_data_for_direction(user_data):
        # TODO: good message
        await message.answer("Validation error")
        await state.clear()
        return

    del user_data["with_return"]
    direction = FlightDirection(**user_data)
    tickets_api = AviasalesTicketsApi(http_session_maker)
    uow = SqlAlchemyUnitOfWork(session_maker)
    try:
        tickets, direction_id = await track(user_id, direction, tickets_api, uow)
    except TicketsAPIConnectionError:
        text = f'{i18n.translate("smth_went_wrong")} 😔 \n {i18n.translate("try_search_again")} 🔄'
        await message.answer(text, reply_markup=user_home_kb.keyboard)
    except DuplicatedFlightDirection as e:
        logger.warning(
            "User tried to add the same direction second time",
            user_id=e.user_id,
            direction=e.flight_direction,
            direction_id=e.direction_id,
        )
        await message.answer(
            i18n.translate("you_already_track_this_direction"),
            reply_markup=user_home_kb.keyboard,
        )
    except Exception as e:
        logger.exception(e)
        text = f'{i18n.translate("smth_went_wrong")} 😔 \n {i18n.translate("we_fixing_this")} 🔄'
        await message.answer(text, reply_markup=user_home_kb.keyboard)
    else:
        await message.answer(
            text=f"✅ {i18n.translate('direction_added_here_are_tickets')}\n👇👇👇"
        )
        await message.answer(
            text=ticket_view.print_tickets(tickets, direction),
            parse_mode="html",
            disable_web_page_preview=True,
            reply_markup=show_low_prices_calendar_keyboard(direction_id),
        )
    finally:
        await state.clear()
