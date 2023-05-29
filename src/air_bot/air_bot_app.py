import asyncio
import logging.config
from typing import Dict, Optional, Any

import aiohttp

from air_bot.aiohttp_logging import get_trace_config
from air_bot.bot import BotService
from air_bot.config import config
from air_bot.db.db_manager import DBManager
from delayed_keyboard_interrupt import DelayedKeyboardInterrupt  # type: ignore[import]

logger = logging.getLogger(__name__)


class AirBotApp:
    def __init__(self) -> None:
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._wait_event: Optional[asyncio.Event] = None
        self._wait_task: Optional[asyncio.Task] = None  # type: ignore[type-arg]

        self._db_manager: Optional[DBManager] = None
        self._aiohttp_client_session: Optional[aiohttp.ClientSession] = None
        self._bot: Optional[BotService] = None

    def run(self) -> None:
        self._loop = asyncio.new_event_loop()

        try:
            try:
                with DelayedKeyboardInterrupt(propagate_to_forked_processes=True):
                    self._start()
            except KeyboardInterrupt:
                logger.info("!!! AirBotApp.run: got KeyboardInterrupt during start")
                raise
            logger.info("AirBotApp.run: entering wait loop")
            self._wait()
            logger.info("AirBotApp.run: exiting wait loop")
        except KeyboardInterrupt:
            try:
                with DelayedKeyboardInterrupt(propagate_to_forked_processes=True):
                    self._stop()
            except KeyboardInterrupt:
                logger.info("!!! AirBotApp.run: got KeyboardInterrupt during stop")

    async def _astart(self) -> None:
        self._db_manager = DBManager(config)
        self._aiohttp_client_session = aiohttp.ClientSession(
            trace_configs=[get_trace_config()]
        )
        self._bot = BotService(config, self._db_manager, self._aiohttp_client_session)

        await self._db_manager.start()
        await self._bot.start()

    async def _astop(self) -> None:
        await self._aiohttp_client_session.close()  # type: ignore[union-attr]
        await self._db_manager.stop()  # type: ignore[union-attr]

    async def _await(self) -> None:
        self._wait_event = asyncio.Event()
        self._wait_task = asyncio.create_task(self._wait_event.wait())
        await self._wait_task

    def _start(self) -> None:
        self._loop.run_until_complete(self._astart())  # type: ignore[union-attr]

    def _stop(self) -> None:
        self._loop.run_until_complete(self._astop())  # type: ignore[union-attr]

        if self._wait_event:
            self._wait_event.set()

        if self._wait_task:
            self._loop.run_until_complete(self._wait_task)  # type: ignore[union-attr]

        def __loop_exception_handler(loop, context: Dict[str, Any]):  # type: ignore[no-untyped-def]
            if type(context["exception"]) == ConnectionResetError:
                logger.info(
                    "!!! AirBotApp._stop.__loop_exception_handler: suppressing ConnectionResetError"
                )
            elif type(context["exception"]) == OSError:
                logger.info(
                    "!!! AirBotApp._stop.__loop_exception_handler: suppressing OSError"
                )
            else:
                logger.info(
                    "!!! AirBotApp._stop.__loop_exception_handler: unhandled exception: {context}"
                )

        self._loop.set_exception_handler(__loop_exception_handler)  # type: ignore[union-attr]

        try:
            self._cancel_all_tasks()
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())  # type: ignore[union-attr]
        finally:
            logger.info("AirBotApp._stop: closing event loop")
            self._loop.close()  # type: ignore[union-attr]

    def _wait(self) -> None:
        self._loop.run_until_complete(self._await())  # type: ignore[union-attr]

    def _cancel_all_tasks(self) -> None:
        to_cancel = asyncio.tasks.all_tasks(self._loop)
        logger.info(
            f"AirBotApp._cancel_all_tasks: cancelling {len(to_cancel)} tasks ..."
        )

        if not to_cancel:
            return

        for task in to_cancel:
            task.cancel()

        self._loop.run_until_complete(  # type: ignore[union-attr]
            asyncio.tasks.gather(  # type: ignore[call-overload]
                *to_cancel, loop=self._loop, return_exceptions=True
            )
        )

        for task in to_cancel:
            if task.cancelled():
                continue

            if task.exception() is not None:
                self._loop.call_exception_handler(  # type: ignore[union-attr]
                    {
                        "message": "unhandled exception during AirBotApp.run() shutdown",
                        "exception": task.exception(),
                        "task": task,
                    }
                )
