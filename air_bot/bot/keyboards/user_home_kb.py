from aiogram import types

from air_bot.bot.i18n import Translator


def user_home_keyboard(i18n: Translator) -> types.ReplyKeyboardMarkup:
    kb = [
        [
            types.KeyboardButton(text=f'🔍 {i18n.translate("new_search")}'),
            types.KeyboardButton(text=f'⚙️ {i18n.translate("personal_account")}'),
        ]
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
