from aiogram import types


def flight_direction_actions(flight_direction_id: int) -> types.InlineKeyboardMarkup:
    kb = [
        [
            types.InlineKeyboardButton(
                text="ℹ️ Подробная информация",
                callback_data=f"show_direction_info|{flight_direction_id}",
            ),
            types.InlineKeyboardButton(
                text="❌ Удалить",
                callback_data=f"delete_direction|{flight_direction_id}",
            ),
        ]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=kb)
