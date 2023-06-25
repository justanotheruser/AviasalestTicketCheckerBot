import asyncio

from apscheduler.schedulers.async_ import AsyncScheduler
from apscheduler.triggers.interval import IntervalTrigger

from air_bot.service.direction_updater import DirectionUpdater
from air_bot.settings import Interval, SettingsStorage


class ServiceScheduler:
    def __init__(
        self,
        scheduler: AsyncScheduler,
        setting_storage: SettingsStorage,
        settings_changed: asyncio.Event,
        direction_updater: DirectionUpdater,
    ):
        self.scheduler = scheduler
        self.setting_storage = setting_storage
        self.settings_changed = settings_changed
        self.direction_updater = direction_updater
        self.direction_updater_schedule = None

    async def start(self):
        await self.scheduler.start_in_background()
        await self._schedule()
        await self.scheduler.add_schedule(
            self.setting_storage.reload, IntervalTrigger(seconds=5)
        )
        asyncio.create_task(self._monitor_settings_change())

    async def _schedule(self):
        if self.direction_updater_schedule:
            await self.scheduler.remove_schedule(self.direction_updater_schedule)
        scheduler_settings = self.setting_storage.settings.scheduler
        interval = scheduler_settings.directions_update_interval
        if scheduler_settings.directions_update_interval_units == Interval.MINUTES:
            trigger = IntervalTrigger(minutes=interval)
        else:
            trigger = IntervalTrigger(seconds=interval)
        self.direction_updater_schedule = await self.scheduler.add_schedule(
            self.direction_updater.update, trigger
        )
        pass

    async def _monitor_settings_change(self):
        while True:
            await self.settings_changed.wait()
            await self._schedule()
            self.settings_changed.clear()
