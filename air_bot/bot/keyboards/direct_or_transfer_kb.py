from functools import cached_property

from aiogram import types

from air_bot.bot.i18n import i18n


class DirectOrTransferKb:
    direct_flights_cb_data = "without_transfer"
    transfer_flights_cb_data = "with_transfer"

    @cached_property
    def direct_flights_btn_text(self) -> str:
        return f"➡️ {i18n.translate('direct_flights')}"

    @cached_property
    def transfer_flights_btn_text(self) -> str:
        return f"↕️️ {i18n.translate('transfer_flights')}"

    @cached_property
    def keyboard(self) -> types.InlineKeyboardMarkup:
        kb = [
            [
                types.InlineKeyboardButton(
                    text=self.direct_flights_btn_text,
                    callback_data=self.direct_flights_cb_data
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=self.transfer_flights_btn_text,
                    callback_data=self.transfer_flights_cb_data
                )
            ],
        ]
        return types.InlineKeyboardMarkup(inline_keyboard=kb)


direct_or_transfer_kb = DirectOrTransferKb()
