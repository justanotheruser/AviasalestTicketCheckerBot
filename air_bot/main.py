from loguru import logger

from air_bot.app import App


def main():
    logger.add(
        "logs/air_bot_{time}.log",
        rotation="1 day",
        retention="7 days",
        compression="zip",
    )
    app = App()
    app.run()


if __name__ == "__main__":
    main()
