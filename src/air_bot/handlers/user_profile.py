import logging

from aiogram import Router
from aiogram.filters import Text
from aiogram.types import CallbackQuery, Message

from air_bot.aviasales_api.api_layer import AviasalesAPILayer
from air_bot.checker.ticket_price_checker import TicketPriceChecker
from air_bot.db import DB
from air_bot.keyboards.user_home_kb import user_home_keyboard
from air_bot.keyboards.user_profile_kb import flight_direction_actions
from air_bot.utils.tickets import print_ticket

logger = logging.getLogger("AirBot")

router = Router()


@router.message(Text(text="⚙️ личный кабинет"))
@router.message(commands=["settings", "настройки"])
async def show_user_flight_directions(message: Message, db: DB) -> None:
    user_id = message.from_user.id  # type: ignore[union-attr]
    directions_full = db.get_users_flight_directions(user_id)
    await message.answer("Отслеживаемые направления 👇:")
    if not directions_full:
        return
    for direction_full in directions_full:
        direction = direction_full.direction
        with_or_without_return = (
            "➡️⬅️ Туда и обратно" if direction.return_at else "➡️ В один конец"
        )
        direction_type = "С пересадкой" if direction.with_transfer else "Прямые"
        if direction.return_at:
            header = f"{direction.start_name} - {direction.end_name} - {direction.start_name}"
            dates = (
                f"🕛 Отслеживать за период:\n"
                f"      отправление туда {direction.departure_at}\n"
                f"      отправление обратно {direction.return_at}"
            )
        else:
            header = f"{direction.start_name} - {direction.end_name}"
            dates = f"🕛 Отслеживать за период: {direction.departure_at}"
        text = f"📍 {header}\n{with_or_without_return}\n🔄{direction_type}\n{dates}"
        await message.answer(
            text, reply_markup=flight_direction_actions(direction_full.id)
        )


@router.callback_query(Text(text_startswith="show_direction_info"))
async def show_direction_info(
    callback: CallbackQuery, db: DB, aviasales_api: AviasalesAPILayer
) -> None:
    _, direction_id = callback.data.split("|")  # type: ignore[union-attr]
    direction_id = int(direction_id)
    direction = db.get_users_flight_direction(callback.from_user.id, direction_id)
    ticket = await aviasales_api.get_cheapest_ticket(direction)
    if not ticket:
        await callback.message.answer("Рейсов нет!", reply_markup=user_home_keyboard())  # type: ignore[union-attr]
    else:
        text = print_ticket(ticket, direction)
        await callback.message.answer(  # type: ignore[union-attr]
            text=text,
            parse_mode="html",
            disable_web_page_preview=True,
            reply_markup=user_home_keyboard(),
        )
    await callback.answer()


@router.callback_query(Text(text_startswith="delete_direction"))
async def delete_direction(
    callback: CallbackQuery, db: DB, ticket_price_checker: TicketPriceChecker
) -> None:
    _, direction_id = callback.data.split("|")  # type: ignore[union-attr]
    direction_id = int(direction_id)
    direction = db.get_users_flight_direction(callback.from_user.id, direction_id)
    db.delete_users_flight_direction(callback.from_user.id, direction_id)
    ticket_price_checker.remove_check(callback.from_user.id, direction)
    await callback.message.answer(  # type: ignore[union-attr]
        "Направление удалено! 🗑",
        reply_markup=user_home_keyboard(),
    )
    await callback.answer()
