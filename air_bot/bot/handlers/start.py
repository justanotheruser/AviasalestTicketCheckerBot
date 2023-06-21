from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from air_bot.bot.i18n import i18n
from air_bot.bot.keyboards.add_flight_direction_kb import add_flight_direction_kb
from air_bot.bot.keyboards.user_home_kb import user_home_kb
from air_bot.service.users_service import add_user
from air_bot.adapters.repo.session_maker import AbstractSessionMaker
from air_bot.adapters.repo.uow import SqlAlchemyUnitOfWork
router = Router()


@router.message(Command(commands=["start"]))
async def start(message: Message, session_maker: AbstractSessionMaker) -> None:
    await add_user(message.from_user.id, SqlAlchemyUnitOfWork(session_maker))
    await message.answer(
        i18n.translate(
            "start_greeting", username=message.from_user.first_name
        ),  # type: ignore[union-attr]
        reply_markup=user_home_kb.keyboard,
    )
    await message.answer(
        i18n.translate("start_сall_to_action"),
        reply_markup=add_flight_direction_kb.keyboard,
    )
