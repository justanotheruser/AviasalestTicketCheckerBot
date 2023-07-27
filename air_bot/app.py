import asyncio

from apscheduler.schedulers.async_ import AsyncScheduler

from air_bot.adapters.repo.session_maker import SessionMaker
from air_bot.bot.service import BotService
from air_bot.config import config
from air_bot.graceful_shutdown.service import ServiceWithGracefulShutdown
from air_bot.http_session import HttpSessionMaker
from air_bot.service.direction_updater import DirectionUpdater
from air_bot.service.scheduler import ServiceScheduler
from air_bot.settings import SettingsStorage


class App(ServiceWithGracefulShutdown):
    def __init__(self):
        super().__init__()
        self.session_maker = SessionMaker()
        self.http_session_maker = HttpSessionMaker()
        self.settings_changed_event = asyncio.Event()
        self.settings_storage = SettingsStorage(
            config.settings_file_path, self.settings_changed_event
        )
        self.bot = BotService(
            config, self.http_session_maker, self.session_maker, self.settings_storage
        )
        self.direction_updater = DirectionUpdater(
            self.settings_storage, self.bot, self.session_maker, self.http_session_maker
        )

    async def start(self):
        async with AsyncScheduler() as scheduler:
            service_scheduler = ServiceScheduler(
                scheduler,
                self.settings_storage,
                self.settings_changed_event,
                self.direction_updater,
            )
            await self.session_maker.start()
            await service_scheduler.start()
            asyncio.create_task(self.bot.start())

    async def stop(self):
        self.http_session_maker.close()
        await self.session_maker.stop()
