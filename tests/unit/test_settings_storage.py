import asyncio
import textwrap

from air_bot.settings import (
    DirectionUpdaterSettings,
    Interval,
    SchedulerSetting,
    Settings,
    SettingsStorage,
    UsersSettings,
)


def test_read_settings(tmp_path):
    settings_file = tmp_path / "test_settings.ini"
    settings_file.write_text(
        textwrap.dedent(
            """
        [scheduler]
        directions_update_interval = 5
        directions_update_interval_units = minutes
        
        [direction_updater]
        needs_update_after = 60
        max_directions_for_single_update = 3900
        
        [users]
        max_directions_per_user = 10
        price_reduction_threshold_percents = 5
    """
        )
    )
    storage = SettingsStorage(settings_file, asyncio.Event())
    assert storage.settings == Settings(
        SchedulerSetting(
            directions_update_interval=5,
            directions_update_interval_units=Interval.MINUTES,
        ),
        DirectionUpdaterSettings(
            needs_update_after=60, max_directions_for_single_update=3900
        ),
        UsersSettings(max_directions_per_user=10, price_reduction_threshold_percents=5),
    )
