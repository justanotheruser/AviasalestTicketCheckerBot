from loguru import logger

from air_bot.bot.service import BotService
from air_bot.settings import SettingsStorage


class DirectionUpdater:
    def __init__(
        self,
        settings_storage: SettingsStorage,
        bot: BotService,
        session_maker,
        http_session_maker,
    ):
        self.settings_storage = settings_storage
        self.bot = bot
        self.session_maker = session_maker
        self.http_session_maker = http_session_maker

    async def update(self):
        logger.info("Starting direction update")
