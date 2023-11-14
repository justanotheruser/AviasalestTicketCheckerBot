from loguru import logger

from air_bot.app import App
from air_bot.config import config


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
    app = App()
    app.run()


if __name__ == "__main__":
    main()
