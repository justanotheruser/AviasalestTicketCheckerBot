import aiohttp

from air_bot.bot.service import BotService
from air_bot.config import config
from air_bot.graceful_shutdown.service import ServiceWithGracefulShutdown


class App(ServiceWithGracefulShutdown):
    def __init__(self):
        super().__init__()

    async def start(self):
        self._aiohttp_client_session = aiohttp.ClientSession()
        self._bot = BotService(config, self._aiohttp_client_session)
        self._bot.start()

    async def stop(self):
        await self._aiohttp_client_session.close()
