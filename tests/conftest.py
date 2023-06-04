import logging

import pytest
from _pytest.logging import caplog as _caplog
from loguru import logger


@pytest.fixture
def caplog(_caplog):
    class PropagateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    logger.add(PropagateHandler(), format="{message}")
    yield _caplog
