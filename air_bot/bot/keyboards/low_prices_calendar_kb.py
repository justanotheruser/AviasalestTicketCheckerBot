from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from air_bot.bot.i18n import i18n


def show_low_prices_calendar_keyboard(flight_direction_id: int) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text=f"📅 {i18n.translate('low_price_calendar')}",
                callback_data=f"show_low_prices_calendar|{flight_direction_id}",
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def low_prices_calendar_nav_keyboard(
    show_prev_button: bool, show_next_button: bool
) -> InlineKeyboardMarkup:
    kb: list[list[InlineKeyboardButton]] = [[]]
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
