from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from air_bot.bot.i18n import i18n
from air_bot.bot.keyboards.add_flight_direction_kb import add_flight_direction_kb
from air_bot.bot.keyboards.user_home_kb import user_home_kb
from air_bot.service.users_service import add_user

router = Router()


@router.message(Command(commands=["start"]))
async def start(message: Message) -> None:
    # TODO: test for int64
    await add_user(message.from_user.id)
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
