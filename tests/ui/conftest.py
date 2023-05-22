from typing import Optional, Union

import pytest
from aiogram import Bot
from aiogram.types import (
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    ForceReply,
)
from aiogram.types.base import UNSET

from bot_config import config


class TestBot(Bot):
    async def send_message(self, *args, **kwargs):
        chat_id = config.channel_id.get_secret_value()
        if "chat_id" in kwargs:
            kwargs["chat_id"] = chat_id
        else:
            args = (chat_id, *args[1:])
        await super().send_message(*args, **kwargs)


class TestMessage:
    def __init__(self, test_bot: TestBot):
        self.bot = test_bot

    async def answer(
        self,
        text: str,
        parse_mode: Optional[str] = UNSET,
        disable_web_page_preview: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        reply_markup: Optional[
            Union[
                InlineKeyboardMarkup,
                ReplyKeyboardMarkup,
                ReplyKeyboardRemove,
                ForceReply,
            ]
        ] = None,
    ):
        chat_id = config.channel_id.get_secret_value()
        await self.bot.send_message(
            chat_id,
            text,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
        )


@pytest.fixture
def bot():
    return TestBot(token=config.bot_token.get_secret_value())


@pytest.fixture
def message_for_answer(bot: TestBot):
    return TestMessage(bot)
