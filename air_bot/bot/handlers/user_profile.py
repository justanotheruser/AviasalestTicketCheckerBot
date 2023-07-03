from aiogram import Router
from aiogram.filters import Command, Text
from aiogram.types import CallbackQuery, Message

from air_bot.adapters.repo.uow import SqlAlchemyUnitOfWork
from air_bot.bot.i18n import i18n
from air_bot.bot.keyboards.user_home_kb import user_home_kb
from air_bot.bot.keyboards.user_profile_kb import flight_direction_actions
from air_bot.bot.presentation.directions import print_direction
from air_bot.bot.presentation.tickets import TicketView
from air_bot.service.user import get_user_directions

router = Router()


@router.message(Text(text=user_home_kb.personal_account_btn_text))
@router.message(Command(commands=["settings", "настройки"]))
async def show_user_flight_directions(message: Message, session_maker) -> None:
    await message.answer(f"{i18n.translate('tracked_directions')} 👇:")
    user_id = message.from_user.id  # type: ignore[union-attr]
    uow = SqlAlchemyUnitOfWork(session_maker)
    users_directions = await get_user_directions(user_id, uow)
    if not users_directions:
        return
    for direction_info in users_directions:
        await message.answer(
            print_direction(direction_info),
            reply_markup=flight_direction_actions(direction_info.id),
        )


@router.callback_query(Text(text_startswith="show_direction_info"))
async def show_direction_info(
    callback: CallbackQuery,
    session_maker,
    ticket_view: TicketView,
) -> None:
    _, direction_id = callback.data.split("|")  # type: ignore[union-attr]
    direction_id = int(direction_id)
    uow = SqlAlchemyUnitOfWork(session_maker)
    async with uow:
        tickets = await uow.tickets.get_direction_tickets(direction_id, limit=1)
        await uow.commit()
    if not tickets:
        await callback.message.answer(  # type: ignore[union-attr]
            "Рейсов нет!",
            # reply_markup=show_low_prices_calendar_keyboard(direction_id)
        )
        await callback.answer()
        return

    cheapest_ticket = tickets[0]
    async with uow:
        direction_info = await uow.flight_directions.get_direction_info(direction_id)
        await uow.commit()

    text = ticket_view.print_ticket(cheapest_ticket, direction_info.direction)
    await callback.message.answer(  # type: ignore[union-attr]
        text=text,
        parse_mode="html",
        disable_web_page_preview=True,
        # reply_markup=show_low_prices_calendar_keyboard(direction_id),
    )
    await callback.answer()


@router.callback_query(Text(text_startswith="delete_direction"))
async def delete_direction(
    callback: CallbackQuery,
    session_maker,
) -> None:
    _, direction_id = callback.data.split("|")  # type: ignore[union-attr]
    direction_id = int(direction_id)
    uow = SqlAlchemyUnitOfWork(session_maker)
    async with uow:
        await uow.users_directions.remove(callback.from_user.id, direction_id)
        await uow.commit()
    await callback.message.answer(  # type: ignore[union-attr]
        f"{i18n.translate('direction_deleted')}! 🗑",
        reply_markup=user_home_kb.keyboard,
    )
    await callback.answer()
