from datetime import datetime
from typing import Tuple

import pytest
import pytest_asyncio

from air_bot.http_session import HttpSessionMaker


@pytest_asyncio.fixture
async def http_session_maker():
    return HttpSessionMaker()


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
