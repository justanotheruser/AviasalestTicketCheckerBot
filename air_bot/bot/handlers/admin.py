from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command(commands=["remove_outdated"]))
async def remove_outdated_directions(message: Message):
    """Manually starts process of removing directions with a past departure date"""
    await message.answer("Hello there!")
