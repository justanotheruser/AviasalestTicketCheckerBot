from loguru import logger

from aiogram import Router
from aiogram.filters import Text
from aiogram.types import CallbackQuery, Message
from air_bot.bot.keyboards.user_home_kb import user_home_kb


router = Router()


@router.message(Text(text=user_home_kb.new_search_btn_text))
@router.message(commands=["settings", "настройки"])
async def show_user_flight_directions(message: Message, session_maker) -> None:
    user_id = message.from_user.id  # type: ignore[union-attr]
    await message.answer("Отслеживаемые направления 👇:")
    session = session_maker()


'''
@router.message(Text(text="⚙️ личный кабинет"))
@router.message(commands=["settings", "настройки"])
async def show_user_flight_directions(message: Message) -> None:
    user_id = message.from_user.id  # type: ignore[union-attr]
    users_directions = await db_manager.get_users_flight_directions(user_id)
    await message.answer("Отслеживаемые направления 👇:")
    if not users_directions:
        return
    for direction in users_directions:
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
        await message.answer(text, reply_markup=flight_direction_actions(direction.id))


@router.callback_query(Text(text_startswith="show_direction_info"))
async def show_direction_info(
    callback: CallbackQuery, db_manager: DBManager, aviasales_api: AviasalesAPILayer
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
    ticket, success = await aviasales_api.get_cheapest_ticket(direction)
    if not success:
        await callback.message.answer(  # type: ignore[union-attr]
            "Произошла ошибка, попробуйте ещё раз чуть позже",
            reply_markup=user_home_keyboard(),
        )
        await callback.answer()
        return
    if not ticket:
        await callback.message.answer(  # type: ignore[union-attr]
            "Рейсов нет!", reply_markup=show_low_prices_calendar_keyboard(direction_id)
        )
    else:
        text = print_ticket(ticket, direction)
        await callback.message.answer(  # type: ignore[union-attr]
            text=text,
            parse_mode="html",
            disable_web_page_preview=True,
            reply_markup=show_low_prices_calendar_keyboard(direction_id),
        )
    await callback.answer()


@router.callback_query(Text(text_startswith="delete_direction"))
async def delete_direction(
    callback: CallbackQuery,
    db_manager: DBManager,
    ticket_price_checker: TicketPriceChecker,
) -> None:
    _, direction_id = callback.data.split("|")  # type: ignore[union-attr]
    direction_id = int(direction_id)
    user_direction = await db_manager.get_users_flight_direction(
        callback.from_user.id, direction_id
    )
    if not user_direction:
        await callback.answer("Кнопка устарела")
        return
    success = await db_manager.delete_users_flight_direction(
        callback.from_user.id, direction_id
    )
    if not success:
        await callback.answer(text="Что-то пошло не так. Повторите попытку позже")
        return
    direction = flight_direction_from_db_type(user_direction)
    ticket_price_checker.remove_check(callback.from_user.id, direction)
    await callback.message.answer(  # type: ignore[union-attr]
        "Направление удалено! 🗑",
        reply_markup=user_home_keyboard(),
    )
    await callback.answer()
'''