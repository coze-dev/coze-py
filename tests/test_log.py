import logging

import pytest

from cozepy import setup_logging


def test_log():
    with pytest.raises(ValueError):
        setup_logging(123)

    setup_logging(logging.DEBUG)
