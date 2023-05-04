from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from air_bot.keyboards.add_flight_direction_kb import add_flight_direction_keyboard
from air_bot.keyboards.user_home_kb import user_home_keyboard

router = Router()


@router.message(Command(commands=["start"]))
async def start(message: Message) -> None:
    await message.answer(
        f"Привет, {message.from_user.first_name}!",  # type: ignore[union-attr]
        reply_markup=user_home_keyboard(),
    )
    await message.answer(
        "Укажи направление, и я буду отслеживать для тебя самые выгодные цены на авиабилеты. 😉",
        reply_markup=add_flight_direction_keyboard(),
    )
