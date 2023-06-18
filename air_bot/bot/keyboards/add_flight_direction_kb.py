from functools import cached_property

from aiogram import types

from air_bot.bot.i18n import i18n


class AddFlightDirectionKb:
    @cached_property
    def add_direction_btn_text(self) -> str:
        return i18n.translate("add_direction")

    @cached_property
    def keyboard(self) -> types.InlineKeyboardMarkup:
        kb = [
            [
                types.InlineKeyboardButton(
                    text=self.add_direction_btn_text,
                    callback_data="add_flight_direction",
                )
            ]
        ]
        return types.InlineKeyboardMarkup(inline_keyboard=kb)


add_flight_direction_kb = AddFlightDirectionKb()
