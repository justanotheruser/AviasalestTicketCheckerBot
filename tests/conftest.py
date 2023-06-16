import logging

import pytest
from _pytest.logging import caplog as _caplog  # noqa: F401
from loguru import logger


@pytest.fixture
def caplog(_caplog):  # noqa: F811
    class PropagateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    logger.add(PropagateHandler(), format="{message}")
    yield _caplog
