import inspect
import logging

from loguru import logger

from air_bot.app import App
from air_bot.config import config


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def main():
    log_level = "DEBUG" if config.env == "debug" else "INFO"
    logger.add(
        "logs/air_bot_{time}.log",
        rotation="1 day",
        retention="7 days",
        compression="zip",
        level=log_level,
        filter=lambda record: record["extra"].get("name") is None,
    )
    logging.basicConfig(handlers=[InterceptHandler()], level=log_level, force=True)
    app = App()
    app.run()


if __name__ == "__main__":
    main()
