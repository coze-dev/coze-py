from typing import Any, AsyncIterator, List

import pytest

from cozepy.util import anext, base64_encode_string


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
