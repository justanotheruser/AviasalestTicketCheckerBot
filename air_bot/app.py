import asyncio

from apscheduler.schedulers.async_ import AsyncScheduler
from loguru import logger

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
        logger.info(f"Starting with config: {config}")
        self.session_maker = SessionMaker()
        self.http_session_maker = HttpSessionMaker()
        self.settings_changed_event = asyncio.Event()
        self.settings_storage = SettingsStorage(
            config.settings_file_path, self.settings_changed_event
        )
        self.direction_updater = DirectionUpdater(
            self.settings_storage, self.session_maker, self.http_session_maker
        )
        self.bot = BotService(
            config,
            self.http_session_maker,
            self.session_maker,
            self.settings_storage,
            self.direction_updater,
        )
        self.direction_updater.set_user_notifier(self.bot)

    async def start(self):
        await self.session_maker.start()
        asyncio.create_task(self._start_scheduler())
        asyncio.create_task(self.bot.start())

    async def stop(self):
        await self.http_session_maker.close()
        await self.session_maker.stop()

    async def _start_scheduler(self):
        async with AsyncScheduler() as scheduler:
            service_scheduler = ServiceScheduler(
                scheduler,
                self.settings_storage,
                self.settings_changed_event,
                self.direction_updater,
            )
            await service_scheduler.start()
            while True:
                await asyncio.sleep(1)
