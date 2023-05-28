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


def low_prices_calendar_nav_keyboard(
    show_prev_button: bool, show_next_button: bool
) -> InlineKeyboardMarkup:
    kb = [[]]
    if show_prev_button:
        kb[0].append(
            InlineKeyboardButton(
                text="<<<", callback_data="low_prices_calendar__prev_month"
            )
        )
    if show_next_button:
        kb[0].append(
            InlineKeyboardButton(
                text=">>>", callback_data="low_prices_calendar__next_month"
            )
        )
    return InlineKeyboardMarkup(inline_keyboard=kb)
