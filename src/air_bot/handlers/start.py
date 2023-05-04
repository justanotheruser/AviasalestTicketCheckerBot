from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from air_bot.keyboards.add_direction import get_add_direction_keyboard
from air_bot.keyboards.user_home import get_user_home_keyboard

router = Router()


@router.message(Command(commands=['start']))
async def start(message: Message):
    await message.answer(f'Привет, {message.from_user.first_name}!',
                         reply_markup=get_user_home_keyboard())
    await message.answer('Укажи направление, и я буду отслеживать для тебя самые выгодные цены на авиабилеты. 😉',
                         reply_markup=get_add_direction_keyboard())
