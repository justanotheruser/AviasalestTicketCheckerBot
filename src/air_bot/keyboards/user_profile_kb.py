from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def flight_direction_actions(flight_direction_id: int) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text="ℹ️ Подробная информация",
                callback_data=f"show_direction_info|{flight_direction_id}",
            ),
            InlineKeyboardButton(
                text="❌ Удалить",
                callback_data=f"delete_direction|{flight_direction_id}",
            ),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
