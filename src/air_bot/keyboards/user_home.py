from aiogram import types


def get_user_home_keyboard():
    kb = [[types.KeyboardButton(text='🔍 новый поиск'), types.KeyboardButton(text='⚙️ личный кабинет')]]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
