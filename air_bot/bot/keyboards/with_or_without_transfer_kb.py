from datetime import datetime
from functools import cached_property

from aiogram import types

from air_bot.domain.model import Location
from air_bot.bot.i18n import i18n


class WithOrWithoutTransferKb:
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


with_or_without_transfer_kb = WithOrWithoutTransferKb()


def choose_airport_keyboard(locations: list[Location]) -> types.InlineKeyboardMarkup:
    kb = []
    for location in locations:
        text = f"{location.name} ({location.code})"
        callback_data = f"{location.name}|{location.code}"
        kb.append([types.InlineKeyboardButton(text=text, callback_data=callback_data)])
    return types.InlineKeyboardMarkup(inline_keyboard=kb)


def choose_month_keyboard() -> types.InlineKeyboardMarkup:
    month_number2name = {
        1: "январь",
        2: "февраль",
        3: "март",
        4: "апрель",
        5: "май",
        6: "июнь",
        7: "июль",
        8: "август",
        9: "сентябрь",
        10: "октябрь",
        11: "ноябрь",
        12: "декабрь",
    }
    current_month = datetime.now().month
    current_year = datetime.now().year
    months = list(range(1, 13))
    while months[0] != current_month:
        months.append(months.pop(0))
    month_idx = 0
    year_delta = 0
    kb = []
    for _ in range(3):
        row = []
        for _ in range(4):
            month = months[month_idx]
            year = current_year + year_delta
            year_month = f"{year}-{month:02}"
            row.append(
                types.InlineKeyboardButton(
                    text=month_number2name[month], callback_data=year_month
                )
            )
            if months[month_idx] == 12:
                year_delta = 1
            month_idx += 1
        kb.append(row)
    return types.InlineKeyboardMarkup(inline_keyboard=kb)
