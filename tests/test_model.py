from typing import Dict

import pytest

from cozepy import CozeEventError, LastIDPaged, NumberPaged, Stream, TokenPaged
from cozepy.model import AsyncStream
from cozepy.util import anext

from .test_util import to_async_iterator


def test_page_mode():
    page = TokenPaged(["a", "b", "c"], "next_page", True)
    assert f"{page}" == "TokenPaged(items=['a', 'b', 'c'], next_page_token=next_page)"

    page = NumberPaged(["a", "b", "c"], 1, 3, 100)
    assert f"{page}" == "NumberPaged(items=['a', 'b', 'c'], page_num=1, page_size=3, total=100)"

    page = LastIDPaged(["a", "b", "c"], 1, 3, True)
    assert f"{page}" == "LastIDPaged(items=['a', 'b', 'c'], first_id=1, last_id=3, has_more=True)"


def mock_sync_handler(d: Dict[str, str]):
    return d


async def mock_async_handler(d: Dict[str, str]):
    return d


class TestStream:
    def test_stream_invalid_event(self):
        items = ["event:x"]
        s = Stream(iter(items), ["field"], mock_sync_handler, "mocked-logid")

        with pytest.raises(CozeEventError, match="invalid event, data: event:x, logid: mocked-logid"):
            next(s)

    def test_stream_invalid_field(self):
        items = ["event:x1", "event:x2"]
        s = Stream(iter(items), ["event", "second"], mock_sync_handler, "mocked-logid")

        with pytest.raises(CozeEventError, match="invalid event, field: event, data: event:x2, logid: mocked-logid"):
            next(s)


@pytest.mark.asyncio
class TestAsyncStream:
    async def test_stream_invalid_event(self):
        items = ["event:x"]
        s = AsyncStream(to_async_iterator(items), ["field"], mock_async_handler, "mocked-logid")

        with pytest.raises(CozeEventError, match="invalid event, data: event:x, logid: mocked-logid"):
            await anext(s)

    async def test_stream_invalid_field(self):
        items = ["event:x1", "event:x2"]
        s = AsyncStream(to_async_iterator(items), ["event", "second"], mock_async_handler, "mocked-logid")

        with pytest.raises(CozeEventError, match="invalid event, field: event, data: event:x2, logid: mocked-logid"):
            await anext(s)
