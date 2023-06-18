import os
from datetime import datetime
from typing import Tuple

import pytest
from aiohttp import ClientSession
from dotenv import load_dotenv
from pydantic import SecretStr


@pytest.fixture
def token():
    load_dotenv()
    return SecretStr(os.getenv("AIR_BOT_AVIASALES_API_TOKEN"))


@pytest.fixture
def http_session():
    return ClientSession()


def increment_month(year: int, month: int) -> Tuple[int, int]:
    if month < 12:
        month = month + 1
    else:
        year = year + 1
        month = 1
    return year, month


@pytest.fixture
def this_month():
    now = datetime.now()
    return "{year}-{month:02d}".format(year=now.year, month=now.month)


@pytest.fixture
def next_month():
    now = datetime.now()
    year, month = increment_month(now.year, now.month)
    return "{year}-{month:02d}".format(year=year, month=month)


@pytest.fixture
def next_next_month():
    now = datetime.now()
    year, month = increment_month(now.year, now.month)
    year, month = increment_month(year, month)
    return "{year}-{month:02d}".format(year=year, month=month)
