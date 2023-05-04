import os

from pydantic import BaseSettings, SecretStr


class BotConfig(BaseSettings):
    bot_token: SecretStr

    class Config:
        env_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                '.env')
        env_file_encoding = 'utf-8'


config = BotConfig()
