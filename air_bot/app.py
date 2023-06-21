import aiohttp

from air_bot.bot.service import BotService
from air_bot.config import config
from air_bot.graceful_shutdown.service import ServiceWithGracefulShutdown
from air_bot.adapters.repo.session_maker import SessionMaker


class App(ServiceWithGracefulShutdown):
    def __init__(self):
        super().__init__()
        self._session_maker = SessionMaker()
        self._aiohttp_client_session = aiohttp.ClientSession()
        self._bot = BotService(config, self._aiohttp_client_session, self._session_maker)

    async def start(self):
        await self._session_maker.start()
        self._bot.start()

    async def stop(self):
        await self._aiohttp_client_session.close()
        await self._session_maker.stop()
