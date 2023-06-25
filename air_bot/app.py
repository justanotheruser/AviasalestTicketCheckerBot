from air_bot.adapters.repo.session_maker import SessionMaker
from air_bot.bot.service import BotService
from air_bot.config import config
from air_bot.graceful_shutdown.service import ServiceWithGracefulShutdown
from air_bot.http_session import HttpSessionMaker


class App(ServiceWithGracefulShutdown):
    def __init__(self):
        super().__init__()
        self._session_maker = SessionMaker()
        self._http_session_maker = HttpSessionMaker()
        self._bot = BotService(config, self._http_session_maker, self._session_maker)

    async def start(self):
        await self._session_maker.start()
        self._bot.start()

    async def stop(self):
        self._http_session_maker.close()
        await self._session_maker.stop()
