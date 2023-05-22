import os

from pydantic import BaseSettings, SecretStr


class BotConfig(BaseSettings):
    bot_token: SecretStr
    channel_id: SecretStr

    class Config:
        env_file = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "test_bot_config.env"
        )
        env_file_encoding = "utf-8"


config = BotConfig()
