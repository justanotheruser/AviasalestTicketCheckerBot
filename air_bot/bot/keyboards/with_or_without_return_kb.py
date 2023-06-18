from functools import cached_property

from aiogram import types

from air_bot.bot.i18n import i18n


class WithOrWithoutReturnKb:
    one_way_cb_data = "without_return"
    round_trip_cb_data = "with_return"

    @cached_property
    def one_way_ticket_btn_text(self) -> str:
        return f"➡️ {i18n.translate('one_way_ticket')}"

    @cached_property
    def round_trip_ticket_btn_text(self) -> str:
        return f"↔️ {i18n.translate('round_trip_ticket')}"

    @cached_property
    def keyboard(self) -> types.InlineKeyboardMarkup:
        kb = [
            [
                types.InlineKeyboardButton(
                    text=self.one_way_ticket_btn_text,
                    callback_data=self.one_way_cb_data,
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=self.round_trip_ticket_btn_text,
                    callback_data=self.round_trip_cb_data,
                )
            ],
        ]
        return types.InlineKeyboardMarkup(inline_keyboard=kb)


with_or_without_return_kb = WithOrWithoutReturnKb()
