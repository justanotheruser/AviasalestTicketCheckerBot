import asyncio
import logging.config
from typing import Dict, Optional, Any
from air_bot.config import config
from air_bot.db.db_manager import DBManager
from delayed_keyboard_interrupt import DelayedKeyboardInterrupt


logger = logging.getLogger(__name__)


class AsyncService2:
    """
    Dummy service that does nothing.
    """

    def __init__(self):
        pass

    async def start(self):
        logger.info(f'AsyncService2: starting')
        await asyncio.sleep(1)
        logger.info(f'AsyncService2: started')

    async def stop(self):
        logger.info(f'AsyncService2: stopping')
        await asyncio.sleep(1)
        logger.info(f'AsyncService2: stopped')


class AirBotApp:
    def __init__(self):
        self._loop = None  # type: Optional[asyncio.AbstractEventLoop]
        self._wait_event = None  # type: Optional[asyncio.Event]
        self._wait_task = None  # type: Optional[asyncio.Task]

        self._db_manager = None  # type: Optional[AsyncService1]
        self._service2 = None  # type: Optional[AsyncService2]

    def run(self):
        self._loop = asyncio.new_event_loop()

        try:
            try:
                with DelayedKeyboardInterrupt(propagate_to_forked_processes=True):
                    self._start()
            except KeyboardInterrupt:
                logger.info(f'!!! AirBotApp.run: got KeyboardInterrupt during start')
                raise
            logger.info(f'AirBotApp.run: entering wait loop')
            self._wait()
            logger.info(f'AirBotApp.run: exiting wait loop')
        except KeyboardInterrupt:
            try:
                with DelayedKeyboardInterrupt(propagate_to_forked_processes=True):
                    self._stop()
            except KeyboardInterrupt:
                logger.info(f'!!! AirBotApp.run: got KeyboardInterrupt during stop')

    async def _astart(self):
        self._db_manager = DBManager(config)
        self._service2 = AsyncService2()

        await self._db_manager.start()
        await self._service2.start()

    async def _astop(self):
        await self._service2.stop()
        await self._db_manager.stop()

    async def _await(self):
        self._wait_event = asyncio.Event()
        self._wait_task = asyncio.create_task(self._wait_event.wait())
        await self._wait_task

    def _start(self):
        self._loop.run_until_complete(self._astart())

    def _stop(self):
        self._loop.run_until_complete(self._astop())

        if self._wait_event:
            self._wait_event.set()

        if self._wait_task:
            self._loop.run_until_complete(self._wait_task)

        def __loop_exception_handler(loop, context: Dict[str, Any]):
            if type(context['exception']) == ConnectionResetError:
                logger.info(f'!!! AirBotApp._stop.__loop_exception_handler: suppressing ConnectionResetError')
            elif type(context['exception']) == OSError:
                logger.info(f'!!! AirBotApp._stop.__loop_exception_handler: suppressing OSError')
            else:
                logger.info(f'!!! AirBotApp._stop.__loop_exception_handler: unhandled exception: {context}')

        self._loop.set_exception_handler(__loop_exception_handler)

        try:
            self._cancel_all_tasks()
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())
        finally:
            logger.info(f'AirBotApp._stop: closing event loop')
            self._loop.close()

    def _wait(self):
        self._loop.run_until_complete(self._await())

    def _cancel_all_tasks(self):
        to_cancel = asyncio.tasks.all_tasks(self._loop)
        logger.info(f'AirBotApp._cancel_all_tasks: cancelling {len(to_cancel)} tasks ...')

        if not to_cancel:
            return

        for task in to_cancel:
            task.cancel()

        self._loop.run_until_complete(
            asyncio.tasks.gather(*to_cancel, loop=self._loop, return_exceptions=True)
        )

        for task in to_cancel:
            if task.cancelled():
                continue

            if task.exception() is not None:
                self._loop.call_exception_handler({
                    'message': 'unhandled exception during Application.run() shutdown',
                    'exception': task.exception(),
                    'task': task,
                })
