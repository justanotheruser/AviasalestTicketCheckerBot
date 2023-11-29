import asyncio
import logging

from apscheduler.schedulers.async_ import AsyncScheduler
from apscheduler.triggers.cron import CronTrigger
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
        logging.basicConfig()
        logging.getLogger("apscheduler").setLevel(logging.WARN)
        self.scheduler = scheduler
        self.setting_storage = setting_storage
        self.settings_changed = settings_changed
        self.direction_updater = direction_updater
        self.direction_updater_schedule = None
        self.update_cycle_task = None

    async def start(self):
        await self.scheduler.start_in_background()
        await self._schedule_direction_updater()
        await self.scheduler.add_schedule(
            self.setting_storage.reload, IntervalTrigger(seconds=5)
        )
        await self.scheduler.add_schedule(
            self.direction_updater.remove_outdated, CronTrigger(hour=0, minute=1)
        )
        asyncio.create_task(self._monitor_settings_change())

    async def _schedule_direction_updater(self):
        if self.direction_updater_schedule:
            await self.scheduler.remove_schedule(self.direction_updater_schedule)
        settings = self.setting_storage.settings.scheduler
        interval = settings.directions_update_interval
        #if settings.directions_update_interval_units == Interval.MINUTES:
        #    trigger = IntervalTrigger(minutes=interval)
        #else:
        #    trigger = IntervalTrigger(seconds=interval)
        #self.direction_updater_schedule = await self.scheduler.add_schedule(
        #    self.direction_updater.update, trigger
        #)

        if settings.directions_update_interval_units == Interval.MINUTES:
            interval *= 60
        if self.update_cycle_task:
            self.update_cycle_task.cancel()
        self.update_cycle_task = asyncio.create_task(self.update_cycle(interval))

    async def update_cycle(self, interval: int):
        while True:
            await self.direction_updater.update()
            await asyncio.sleep(interval)

    async def _monitor_settings_change(self):
        while True:
            await self.settings_changed.wait()
            await self._schedule_direction_updater()
            self.settings_changed.clear()
