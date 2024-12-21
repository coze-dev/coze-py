from typing import Dict

import httpx
import pytest

from cozepy import AsyncStream, CozeInvalidEventError, ListResponse, Stream
from cozepy.util import anext

from .test_util import mock_response, to_async_iterator


def mock_sync_handler(d: Dict[str, str], logid: str):
    return d


async def mock_async_handler(d: Dict[str, str], logid: str):
    return d


class TestSyncStream:
    def test_sync_stream_invalid_event(self):
        items = ["event:x"]
        response = mock_response()
        s = Stream(response._raw_response, iter(items), ["field"], mock_sync_handler)
        with pytest.raises(CozeInvalidEventError, match="invalid event, data: event:x, logid: " + response.logid):
            next(s)

    def test_stream_invalid_field(self):
        items = ["event:x1", "event:x2"]
        response = mock_response()
        s = Stream(response._raw_response, iter(items), ["event", "second"], mock_sync_handler)

        with pytest.raises(
            CozeInvalidEventError, match="invalid event, field: event, data: event:x2, logid: " + response.logid
        ):
            next(s)


@pytest.mark.asyncio
class TestAsyncStream:
    async def test_asynv_stream_invalid_event(self):
        response = mock_response()
        items = ["event:x"]
        s = AsyncStream(to_async_iterator(items), ["field"], mock_async_handler, response._raw_response)

        with pytest.raises(CozeInvalidEventError, match="invalid event, data: event:x, logid: " + response.logid):
            await anext(s)

    async def test_stream_invalid_field(self):
        response = mock_response()
        items = ["event:x1", "event:x2"]
        s = AsyncStream(to_async_iterator(items), ["event", "second"], mock_async_handler, response._raw_response)

        with pytest.raises(
            CozeInvalidEventError, match="invalid event, field: event, data: event:x2, logid: " + response.logid
        ):
            await anext(s)


class TestListResponse:
    def test_slice(self):
        res = ListResponse(httpx.Response(200), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        # len
        assert len(res) == 10
        # iter
        assert list(res) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        # contains
        assert 1 in res
        assert 11 not in res
        # reversed
        assert list(reversed(res)) == [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        # get item
        assert res[0] == 1
        # get item with slice
        assert res[1:3] == [2, 3]
        # get item with slice and step
        assert res[1:3:2] == [2]
        assert res[1:10:3] == [2, 5, 8]
        # set item
        assert list(res) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        res[1:3] = [11, 12]
        assert list(res) == [1, 11, 12, 4, 5, 6, 7, 8, 9, 10]
        # set item with slice
        res[1:3] = [13, 14, 15]
        assert list(res) == [1, 13, 14, 15, 4, 5, 6, 7, 8, 9, 10]
        # set item with slice and step
        res[1:10:3] = [16, 17, 18]
        assert list(res) == [1, 16, 14, 15, 17, 5, 6, 18, 8, 9, 10]
        # del item
        del res[1]
        assert list(res) == [1, 14, 15, 17, 5, 6, 18, 8, 9, 10]
        # del item with slice
        del res[1:3]
        assert list(res) == [1, 17, 5, 6, 18, 8, 9, 10]
        # del item with slice and step
        del res[1:10:3]
        assert list(res) == [1, 5, 6, 8, 9]
