from typing import List

from aiogram import types

from air_bot.domain.model import Location


def choose_location_keyboard(locations: List[Location]) -> types.InlineKeyboardMarkup:
    kb = []
    for location in locations:
        text = f"{location.name} ({location.code})"
        callback_data = f"{location.name}|{location.code}"
        kb.append([types.InlineKeyboardButton(text=text, callback_data=callback_data)])
    return types.InlineKeyboardMarkup(inline_keyboard=kb)
