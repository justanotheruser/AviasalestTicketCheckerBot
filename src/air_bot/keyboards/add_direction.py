from aiogram import types


def get_add_direction_keyboard():
    kb = [[types.InlineKeyboardButton(text='Добавить направление', callback_data='add_direction')]]
    return types.InlineKeyboardMarkup(inline_keyboard=kb)
