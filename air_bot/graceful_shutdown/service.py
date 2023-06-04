import asyncio
from abc import ABC, abstractmethod

from loguru import logger

from air_bot.graceful_shutdown.delayed_keyboard_interrupt import (
    DelayedKeyboardInterrupt,
)


class ServiceWithGracefulShutdown(ABC):
    def __init__(self):
        self._loop: asyncio.AbstractEventLoop | None = None
        self._wait_event: asyncio.Event | None = None
        self._wait_task: asyncio.Task | None = None

    @abstractmethod
    async def start(self):
        raise NotImplementedError

    @abstractmethod
    async def stop(self):
        raise NotImplementedError

    def run(self):
        self._loop = asyncio.new_event_loop()
        try:
            try:
                with DelayedKeyboardInterrupt(propagate_to_forked_processes=True):
                    self._start()
            except KeyboardInterrupt:
                logger.info("got KeyboardInterrupt during start")
                raise
            logger.info("entering wait loop")
            self._wait()
            logger.info("exiting wait loop")
        except KeyboardInterrupt:
            try:
                with DelayedKeyboardInterrupt(propagate_to_forked_processes=True):
                    self._stop()
            except KeyboardInterrupt:
                logger.info("got KeyboardInterrupt during stop")

    def _start(self):
        self._loop.run_until_complete(self.start())

    def _wait(self):
        self._loop.run_until_complete(self._await())

    async def _await(self):
        self._wait_event = asyncio.Event()
        self._wait_task = asyncio.create_task(self._wait_event.wait())
        await self._wait_task

    def _stop(self):
        self._loop.run_until_complete(self.stop())

        if self._wait_event:
            self._wait_event.set()

        if self._wait_task:
            self._loop.run_until_complete(self._wait_task)

        def __loop_exception_handler(loop, context):
            if "exception" in context:
                if type(context["exception"]) == ConnectionResetError:
                    logger.info(
                        "_stop.__loop_exception_handler: suppressing ConnectionResetError"
                    )
                elif type(context["exception"]) == OSError:
                    logger.info("_stop.__loop_exception_handler: suppressing OSError")
                return

            logger.info(
                f"_stop.__loop_exception_handler: unhandled exception: {context}"
            )

        self._loop.set_exception_handler(__loop_exception_handler)

        try:
            self._cancel_all_tasks()
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())
        finally:
            logger.info("_stop: closing event loop")
            self._loop.close()

    def _cancel_all_tasks(self) -> None:
        to_cancel = asyncio.tasks.all_tasks(self._loop)
        logger.info(f"_cancel_all_tasks: cancelling {len(to_cancel)} tasks ...")

        if not to_cancel:
            return

        for task in to_cancel:
            task.cancel()

        self._loop.run_until_complete(
            asyncio.tasks.gather(*to_cancel, return_exceptions=True)
        )

        for task in to_cancel:
            if task.cancelled():
                continue

            if task.exception() is not None:
                self._loop.call_exception_handler(
                    {
                        "message": "unhandled exception during run() shutdown",
                        "exception": task.exception(),
                        "task": task,
                    }
                )
