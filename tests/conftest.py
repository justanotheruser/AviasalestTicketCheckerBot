import logging

import pytest
from _pytest.logging import caplog as _caplog  # noqa: F401
from loguru import logger

from air_bot.domain.model import FlightDirection


@pytest.fixture
def moscow2spb_one_way_direction():
    return FlightDirection(
        start_code="MOS",
        start_name="Moscow",
        end_code="LEN",
        end_name="Saint-Petersburg",
        with_transfer=False,
        departure_at="2023-05-16",
        return_at=None,
    )


@pytest.fixture
def moscow2antalya_roundtrip_direction():
    return FlightDirection(
        start_code="MOS",
        start_name="Moscow",
        end_code="END",
        end_name="End",
        with_transfer=False,
        departure_at="2023-05-16",
        return_at="2023-06",
    )


@pytest.fixture
def caplog(_caplog):  # noqa: F811
    class PropagateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    logger.add(PropagateHandler(), format="{message}")
    yield _caplog
