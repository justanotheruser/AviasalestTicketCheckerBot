import logging
import logging.config
import os
from datetime import datetime

from dotenv import load_dotenv

from air_bot.air_bot_app import AirBotApp

CONFIG_DIR = "./config"
LOG_DIR = "./logs"

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Load logging configuration"""
    log_configs = {"dev": "logging.dev.ini", "prod": "logging.prod.ini"}
    config = log_configs.get(os.environ["ENV"], "logging.dev.ini")
    config_path = "/".join([CONFIG_DIR, config])

    timestamp = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")

    logging.config.fileConfig(
        config_path,
        disable_existing_loggers=False,
        defaults={"logfilename": f"{LOG_DIR}/{timestamp}.log"},
    )
    schedule_logger = logging.getLogger('schedule')
    schedule_logger.setLevel(level=logging.WARNING)


def main() -> None:
    load_dotenv()
    setup_logging()
    logger.setLevel(logging.INFO)
    logger.info("Starting app")
    app = AirBotApp()
    app.run()
    logger.info("App stopped")


if __name__ == "__main__":
    main()
