from typing import Dict

import pytest

from cozepy import CozeInvalidEventError, Stream
from cozepy.model import AsyncStream
from cozepy.util import anext

from .test_util import to_async_iterator


def mock_sync_handler(d: Dict[str, str]):
    return d


async def mock_async_handler(d: Dict[str, str]):
    return d


class TestStream:
    def test_stream_invalid_event(self):
        items = ["event:x"]
        s = Stream(iter(items), ["field"], mock_sync_handler, "mocked-logid")

        with pytest.raises(CozeInvalidEventError, match="invalid event, data: event:x, logid: mocked-logid"):
            next(s)

    def test_stream_invalid_field(self):
        items = ["event:x1", "event:x2"]
        s = Stream(iter(items), ["event", "second"], mock_sync_handler, "mocked-logid")

        with pytest.raises(
            CozeInvalidEventError, match="invalid event, field: event, data: event:x2, logid: mocked-logid"
        ):
            next(s)


@pytest.mark.asyncio
class TestAsyncStream:
    async def test_stream_invalid_event(self):
        items = ["event:x"]
        s = AsyncStream(to_async_iterator(items), ["field"], mock_async_handler, "mocked-logid")

        with pytest.raises(CozeInvalidEventError, match="invalid event, data: event:x, logid: mocked-logid"):
            await anext(s)

    async def test_stream_invalid_field(self):
        items = ["event:x1", "event:x2"]
        s = AsyncStream(to_async_iterator(items), ["event", "second"], mock_async_handler, "mocked-logid")

        with pytest.raises(
            CozeInvalidEventError, match="invalid event, field: event, data: event:x2, logid: mocked-logid"
        ):
            await anext(s)
