from functools import cached_property

from aiogram import types

from air_bot.bot.i18n import i18n


class UserHomeKb:
    @cached_property
    def new_search_btn_text(self) -> str:
        return f'🔍 {i18n.translate("new_search")}'

    @cached_property
    def personal_account_btn_text(self) -> str:
        return f'⚙️ {i18n.translate("personal_account")}'

    @cached_property
    def keyboard(self) -> types.ReplyKeyboardMarkup:
        kb = [
            [
                types.KeyboardButton(text=self.new_search_btn_text),
                types.KeyboardButton(text=self.personal_account_btn_text),
            ]
        ]
        return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


user_home_kb = UserHomeKb()
