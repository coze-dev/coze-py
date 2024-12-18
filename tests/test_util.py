import os
from typing import Any, AsyncIterator, List

import httpx
import pytest

from cozepy import COZE_COM_BASE_URL
from cozepy.util import anext, base64_encode_string, remove_url_trailing_slash


class ListAsyncIterator:
    def __init__(self, lst: List[Any]):
        self.lst = lst
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.lst):
            raise StopAsyncIteration
        value = self.lst[self.index]
        self.index += 1
        return value


def to_async_iterator(lst: List[Any]) -> AsyncIterator:
    return ListAsyncIterator(lst)


def test_base64_encode_string():
    assert "aGk=" == base64_encode_string("hi")


@pytest.mark.asyncio
async def test_anext():
    async_iterator = to_async_iterator(["mock"])
    assert "mock" == await anext(async_iterator)

    with pytest.raises(StopAsyncIteration):
        await anext(async_iterator)


def test_remove_url_trailing_slash():
    assert remove_url_trailing_slash(None) is None
    assert remove_url_trailing_slash(COZE_COM_BASE_URL) == COZE_COM_BASE_URL
    assert remove_url_trailing_slash(COZE_COM_BASE_URL + "/") == COZE_COM_BASE_URL
    assert remove_url_trailing_slash(COZE_COM_BASE_URL + "//") == COZE_COM_BASE_URL
    assert remove_url_trailing_slash(COZE_COM_BASE_URL + "///") == COZE_COM_BASE_URL


def logid_key():
    return "x-tt-logid"


def make_stream_response(content: str) -> httpx.Response:
    return httpx.Response(
        200,
        headers={"content-type": "text/event-stream", logid_key(): "logid"},
        content=content,
    )


def read_file(path: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, path)

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return content
