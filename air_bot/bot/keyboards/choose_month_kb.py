from datetime import datetime

from aiogram import types

from air_bot.bot.i18n import i18n


class ChooseMonthKb:
    def __init__(self):
        self.month_number2name = {
            1: i18n.translate("january"),
            2: i18n.translate("february"),
            3: i18n.translate("march"),
            4: i18n.translate("april"),
            5: i18n.translate("may"),
            6: i18n.translate("june"),
            7: i18n.translate("july"),
            8: i18n.translate("august"),
            9: i18n.translate("september"),
            10: i18n.translate("october"),
            11: i18n.translate("november"),
            12: i18n.translate("december"),
        }

    def keyboard(self) -> types.InlineKeyboardMarkup:
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
                        text=self.month_number2name[month], callback_data=year_month
                    )
                )
                if months[month_idx] == 12:
                    year_delta = 1
                month_idx += 1
            kb.append(row)
        return types.InlineKeyboardMarkup(inline_keyboard=kb)


choose_month_kb = ChooseMonthKb()
