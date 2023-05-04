from aiogram import types


def user_home_keyboard() -> types.ReplyKeyboardMarkup:
    kb = [
        [
            types.KeyboardButton(text="🔍 новый поиск"),
            types.KeyboardButton(text="⚙️ личный кабинет"),
        ]
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
