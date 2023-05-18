from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def low_prices_calendar_keyboard(flight_direction_id: int) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text="📅 календарь низких цен", callback_data=f"low_prices_calendar|{flight_direction_id}"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
