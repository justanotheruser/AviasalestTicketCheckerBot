import glob
import os
from datetime import datetime
from string import Template

import yaml
from babel.dates import format_datetime
from loguru import logger

from air_bot.config import config


class Translator:
    def __init__(
        self,
        locale: str,
        translations_folder=os.path.join(os.path.dirname(__file__), "locales"),
    ):
        self.data = {}
        self.locale = locale

        files = glob.glob(os.path.join(translations_folder, "*.yaml"))
        for fil in files:
            loc = os.path.splitext(os.path.basename(fil))[0]
            with open(fil, "r", encoding="utf8") as f:
                self.data[loc] = yaml.safe_load(f)

    def set_locale(self, locale):
        if locale in self.data:
            self.locale = locale
        else:
            logger.error(f"Invalid locale: {locale}")

    def get_locale(self):
        return self.locale

    def translate(self, key, **kwargs):
        if self.locale not in self.data:
            logger.error(f"Locale {self.locale} missing key {key}")
            return key
        text = self.data[self.locale].get(key, key)
        if len(kwargs) == 0:
            return text
        return Template(text).safe_substitute(**kwargs)


i18n = Translator(locale=config.locale)


def str_to_datetime(dt_str, datetime_format="%Y-%m-%d"):
    return datetime.strptime(dt_str, datetime_format)


def datetime_to_str(dt, locale: str, datetime_format="MMMM dd, yyyy"):
    return format_datetime(dt, format=datetime_format, locale=locale)
