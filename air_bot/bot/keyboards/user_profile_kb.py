from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from air_bot.bot.i18n import i18n


def flight_direction_actions(flight_direction_id: int) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text=f"ℹ️ {i18n.translate('detailed_information')}",
                callback_data=f"show_direction_info|{flight_direction_id}",
            ),
            InlineKeyboardButton(
                text=f"❌ {i18n.translate('delete_direction')}",
                callback_data=f"delete_direction|{flight_direction_id}",
            ),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
