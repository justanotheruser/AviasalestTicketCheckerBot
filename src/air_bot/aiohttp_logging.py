import logging

import aiohttp

logger = logging.getLogger("aiohttp.client")


def get_trace_config() -> aiohttp.TraceConfig:
    setup_aiohttp_logger()
    trace_config = aiohttp.TraceConfig()
    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_end.append(on_request_end)
    return trace_config


def setup_aiohttp_logger() -> None:
    logger.setLevel(logging.INFO)
    ch = logging.FileHandler("aiohttp.client.log", encoding="utf-8")
    ch.setLevel(logging.INFO)
    ch_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    ch.setFormatter(ch_formatter)
    logger.addHandler(ch)


async def on_request_start(session, context, params) -> None:  # type: ignore[no-untyped-def]
    logger.info(f"Starting request <{params}>")


async def on_request_end(session, context, params) -> None:  # type: ignore[no-untyped-def]
    logger.info(f"Request ended <{params}>")
