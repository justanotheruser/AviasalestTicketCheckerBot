from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def show_low_prices_calendar_keyboard(flight_direction_id: int) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text="📅 календарь низких цен",
                callback_data=f"show_low_prices_calendar|{flight_direction_id}",
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def low_prices_calendar_nav_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text="<<<", callback_data="low_prices_calendar__prev_month"
            ),
            InlineKeyboardButton(
                text=">>>", callback_data="low_prices_calendar__next_month"
            ),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
