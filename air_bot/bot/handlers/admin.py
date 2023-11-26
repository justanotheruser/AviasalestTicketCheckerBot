from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from air_bot.service.direction_updater import DirectionUpdater

router = Router()


@router.message(Command(commands=["remove_outdated"]))
async def remove_outdated_directions(
    message: Message, direction_updater: DirectionUpdater
):
    """Manually starts process of removing directions with a past departure date"""
    n_directions = await direction_updater.remove_outdated()
    await message.answer(f"Removed {n_directions} outdated directions.")
