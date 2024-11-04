"""This module is for settings that can be changed at runtime without stopping the bot"""
import asyncio
import configparser
import contextvars
import functools
from dataclasses import dataclass
from enum import Enum

from loguru import logger


class Interval(Enum):
    SECONDS = 0
    MINUTES = 1


@dataclass(frozen=True)
class SchedulerSetting:
    directions_update_interval: int
    directions_update_interval_units: Interval


@dataclass(frozen=True)
class DirectionUpdaterSettings:
    needs_update_after: int
    max_directions_for_single_update: int


@dataclass(frozen=True)
class UsersSettings:
    max_directions_per_user: int
    price_reduction_threshold_percents: int


@dataclass(frozen=True)
class Settings:
    scheduler: SchedulerSetting
    direction_updater: DirectionUpdaterSettings
    users: UsersSettings


class SettingsStorage:
    def __init__(self, settings_file_path: str, settings_changed: asyncio.Event):
        self.settings_file_path = settings_file_path
        self.settings_changed = settings_changed
        self._settings = read_config(self.settings_file_path)
        logger.info(f"Started with settings: {self._settings}")

    @property
    def settings(self) -> Settings:
        return self._settings

    async def reload(self):
        logger.debug("Reload settings")
        try:
            loaded_settings = await to_thread(read_config, self.settings_file_path)
        except Exception as e:
            logger.error(
                f"Failed to reload settings from {self.settings_file_path}: {e}"
            )
            return
        if loaded_settings != self._settings:
            self._settings = loaded_settings
            self.settings_changed.set()
            logger.info(f"Settings were updated: {self._settings}")


def read_config(filepath: str) -> Settings:
    raw_config = configparser.ConfigParser()
    if not raw_config.read(filepath, encoding="utf-8"):
        raise RuntimeError(f"Can't read settings from {filepath}")
    scheduler = _parse_scheduler_settings(raw_config["scheduler"])
    direction_updater = _parse_direction_updater_settings(
        raw_config["direction_updater"]
    )
    users = _parse_users_settings(raw_config["users"])
    return Settings(
        scheduler=scheduler,
        direction_updater=direction_updater,
        users=users,
    )


def _parse_scheduler_settings(config) -> SchedulerSetting:
    units_str = config["directions_update_interval_units"]
    if units_str == "seconds":
        directions_update_interval_units = Interval.SECONDS
    elif units_str == "minutes":
        directions_update_interval_units = Interval.MINUTES
    else:
        raise RuntimeError(
            f"Unknown directions_update_interval_units value '{units_str}'"
        )
    return SchedulerSetting(
        directions_update_interval=int(config["directions_update_interval"]),
        directions_update_interval_units=directions_update_interval_units,
    )


def _parse_direction_updater_settings(config):
    return DirectionUpdaterSettings(
        needs_update_after=int(config["needs_update_after"]),
        max_directions_for_single_update=int(
            config["max_directions_for_single_update"]
        ),
    )


def _parse_users_settings(config):
    return UsersSettings(
        max_directions_per_user=int(config["max_directions_per_user"]),
        price_reduction_threshold_percents=int(
            config["price_reduction_threshold_percents"]
        ),
    )


async def to_thread(func, /, *args, **kwargs):
    loop = asyncio.get_running_loop()
    ctx = contextvars.copy_context()
    func_call = functools.partial(ctx.run, func, *args, **kwargs)
    return await loop.run_in_executor(None, func_call)
