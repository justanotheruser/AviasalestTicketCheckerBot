import asyncio

from aiogram import Router, F
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from air_bot.bot.i18n import i18n
from air_bot.bot.keyboards.with_or_without_return_kb import with_or_without_return_kb
from air_bot.bot.keyboards.direct_or_transfer_kb import direct_or_transfer_kb
from air_bot.bot.keyboards.choose_location_kb import choose_location_keyboard
#     choose_airport_keyboard,
#     choose_month_keyboard,
from air_bot.bot.keyboards.user_home_kb import user_home_kb
from air_bot.adapters.locations_api import AbstractLocationsApi

# from air_bot.bot.keyboards.low_prices_calendar_kb import show_low_prices_calendar_keyboard
# from air_bot.bot.utils.date import DateReader
# from air_bot.bot.utils.tickets import print_tickets


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
@router.message(Text(text=i18n.translate("cancel"), text_ignore_case=True))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await message.answer(
        text="Добавление маршрута отменено", reply_markup=user_home_kb.keyboard
    )
    await state.clear()


@router.message(Text(text=user_home_kb.new_search_btn_text))
@router.message(Command(commands=["search"]))
async def add_flight_direction(message: Message, state: FSMContext) -> None:
    await message.answer(
        f'{i18n.translate("choose_search_type")} 👇',
        reply_markup=with_or_without_return_kb.keyboard,
    )
    await state.clear()
    await state.set_state(NewDirection.choosing_with_return_or_not)


@router.callback_query(
    NewDirection.choosing_with_return_or_not,
    F.data.in_(
        [
            with_or_without_return_kb.one_way_cb_data,
            with_or_without_return_kb.round_trip_cb_data,
        ]
    ),
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
    F.data.in_([direct_or_transfer_kb.direct_flights_cb_data,
                direct_or_transfer_kb.transfer_flights_cb_data]),
)
async def choose_airport_start(callback: CallbackQuery, state: FSMContext) -> None:
    with_transfer = callback.data == direct_or_transfer_kb.transfer_flights_cb_data
    await state.update_data(with_transfer=with_transfer)
    await callback.message.answer(f"🛫 {i18n.translate('choose_departure_point')}: ")  # type: ignore[union-attr]
    await callback.answer()
    await state.set_state(NewDirection.choosing_airport_start)


@router.message(NewDirection.choosing_airport_start, F.text)
async def choose_specific_airport_start(
    message: Message, state: FSMContext, locations_api: AbstractLocationsApi
) -> None:
    try:
        text: str = message.text  # type: ignore[assignment]
        locations = await locations_api.get_locations(text)
    except Exception:
        response = f"{i18n.translate('smth_went_wrong')} 😔 \n" \
                   f"{i18n.translate('try_again')} 🔄"
        await message.answer(response)
        return
    if not locations:
        response = f"{i18n.translate('no_such_location')} 😔 \n" \
                   f"{i18n.translate('try_again')} 🔄"
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


@router.callback_query()
async def fallback(callback: CallbackQuery):
    print(callback)
