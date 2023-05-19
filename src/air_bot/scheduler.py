import asyncio
from typing import Callable, Coroutine, Any

# TODO: switch to https://github.com/agronholm/apscheduler
import aioschedule as schedule  # type: ignore[import]


class Scheduler:
    def __init__(self) -> None:
        self._job_counter = 0
        self._jobs: dict[int, schedule.Job] = dict()

    def schedule_every_minutes(
        self, interval: int, func: Callable[..., Coroutine[Any, Any, Any]], *args: Any
    ) -> int:
        """Schedule job to run every <interval> minutes. Returns id that can be used for canceling."""
        job_id = self._job_counter
        self._jobs[job_id] = schedule.every(interval).minutes.do(func, *args)
        self._job_counter += 1
        return job_id

    def schedule_every_seconds(
        self, interval: int, func: Callable[..., Coroutine[Any, Any, Any]], *args: Any
    ) -> int:
        """Schedule job to run every <interval> seconds. Returns id that can be used for canceling."""
        job_id = self._job_counter
        self._jobs[job_id] = schedule.every(interval).seconds.do(func, *args)
        self._job_counter += 1
        return job_id

    def cancel(self, job_id: int) -> None:
        job = self._jobs[job_id]
        schedule.cancel_job(job)
        del self._jobs[job_id]

    @staticmethod
    async def run_loop() -> None:
        while True:
            await schedule.run_pending()
            await asyncio.sleep(0.5)
