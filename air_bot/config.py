"""This module is for settings that don't change at runtime"""
import os

from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings


class BotConfig(BaseSettings):
    bot_token: SecretStr
    aviasales_api_token: SecretStr
    aviasales_marker: str
    db_host: str
    db_port: int
    db_user: str
    db_pass: SecretStr
    db_name: str
    locale: str
    currency: str
    settings_file_path: str
    log_level: str
    log_level_sqlalchemy: str = "WARNING"

    class Config:
        env_prefix = "AIR_BOT_"

    def get_mysql_uri(self) -> str:
        uri_template = "mysql+asyncmy://{user}:{password}@{host}:{port}/{db_name}"
        return uri_template.format(
            user=self.db_user,
            password=self.db_pass.get_secret_value(),
            host=self.db_host,
            port=self.db_port,
            db_name=self.db_name,
        )


load_dotenv()
config = BotConfig()  # type: ignore[call-arg]
config.settings_file_path = os.path.expanduser(config.settings_file_path)
