import aiohttp
from loguru import logger

from air_bot.config import config


class HttpSessionMaker:
    def __init__(self):
        # aiohttp.ClientSession() wants to be called inside a coroutine
        self._session: aiohttp.ClientSession | None = None

    def __call__(self):
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession(trace_configs=[get_trace_config()])
        return self._session

    async def close(self):
        if self._session:
            await self._session.close()


def get_trace_config() -> aiohttp.TraceConfig:
    aiohttp_logger = create_aiohttp_logger()
    trace_config = aiohttp.TraceConfig()

    async def on_request_start(session, context, params) -> None:  # type: ignore[no-untyped-def]
        aiohttp_logger.info(f"Starting request <{params}>")

    async def on_request_end(session, context, params) -> None:  # type: ignore[no-untyped-def]
        aiohttp_logger.info(f"Request ended <{params}>")

    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_end.append(on_request_end)
    return trace_config


def create_aiohttp_logger():
    # TODO: configure separately
    log_level = config.log_level
    logger.add(
        "logs/aiohttp_client_{time}.log",
        rotation="1 day",
        retention="7 days",
        compression="zip",
        level=log_level,
        filter=lambda record: record["extra"].get("name") == "aiohttp_client",
    )
    return logger.bind(name="aiohttp_client")
