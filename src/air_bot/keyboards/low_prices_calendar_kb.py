from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def low_prices_calendar_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text="📅 календарь низких цен", callback_data="low_prices_calendar"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
