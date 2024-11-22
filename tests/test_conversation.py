import time

import httpx
import pytest

from cozepy import AsyncCoze, Conversation, Coze, TokenAuth
from cozepy.util import random_hex


def make_conversation():
    return Conversation(id=random_hex(10), created_at=int(time.time()), meta_data={}, last_section_id=random_hex(10))


def mock_list_conversation(respx_mock, has_more, page):
    respx_mock.get(
        "https://api.coze.com/v1/conversations",
        params={
            "page_num": page,
        },
    ).mock(
        httpx.Response(
            200,
            headers={"x-tt-logid": "logid"},
            json={
                "data": {
                    "conversations": [
                        Conversation(
                            id=f"id_{page}", created_at=int(time.time()), meta_data={}, last_section_id=random_hex(10)
                        ).model_dump()
                    ],
                    "has_more": has_more,
                }
            },
        )
    )


@pytest.mark.respx(base_url="https://api.coze.com")
class TestConversation:
    def test_sync_conversations_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        conversation = make_conversation()
        bot_id = random_hex(10)
        respx_mock.post("/v1/conversation/create").mock(httpx.Response(200, json={"data": conversation.model_dump()}))

        res = coze.conversations.create(bot_id=bot_id)
        assert res
        assert res.id == conversation.id
        assert res.last_section_id == conversation.last_section_id

    def test_sync_conversations_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        total = 10
        size = 1
        for idx in range(total):
            mock_list_conversation(respx_mock, has_more=idx + 1 < total, page=idx + 1)

        # no iter
        resp = coze.conversations.list(bot_id="bot id", page_size=1)
        assert resp
        assert resp.has_more is True

        # iter conversation
        total_result = 0
        for idx, conversation in enumerate(coze.conversations.list(bot_id="bot id", page_size=1)):
            total_result += 1
            assert conversation
            assert conversation.id == f"id_{idx + 1}"
        assert total_result == total

        # iter page
        total_result = 0
        for idx, page in enumerate(coze.conversations.list(bot_id="bot id", page_size=1).iter_pages()):
            total_result += 1
            assert page
            assert page.has_more == (idx + 1 < total)
            assert len(page.items) == size
            conversation = page.items[0]
            assert conversation.id == f"id_{idx + 1}"
        assert total_result == total

    def test_sync_conversations_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        conversation = make_conversation()
        respx_mock.get("/v1/conversation/retrieve").mock(httpx.Response(200, json={"data": conversation.model_dump()}))

        res = coze.conversations.retrieve(conversation_id=conversation.id)
        assert res
        assert res.id == conversation.id
        assert res.last_section_id == conversation.last_section_id


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncConversation:
    async def test_async_conversation_create(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        conversation = make_conversation()
        bot_id = random_hex(10)
        respx_mock.post("/v1/conversation/create").mock(httpx.Response(200, json={"data": conversation.model_dump()}))

        res = await coze.conversations.create(bot_id=bot_id)
        assert res
        assert res.id == conversation.id
        assert res.last_section_id == conversation.last_section_id

    async def test_async_conversations_list(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        total = 10
        size = 1
        for idx in range(total):
            mock_list_conversation(respx_mock, has_more=idx + 1 < total, page=idx + 1)

        # no iter
        resp = await coze.conversations.list(bot_id="bot id", page_size=1)
        assert resp
        assert resp.has_more is True

        # iter conversation
        total_result = 0
        resp = await coze.conversations.list(bot_id="bot id", page_size=1)
        for idx, conversation in enumerate([bot async for bot in resp]):
            total_result += 1
            assert conversation
            assert conversation.id == f"id_{idx + 1}"
        assert total_result == total

        # iter page
        total_result = 0
        resp = await coze.conversations.list(bot_id="bot id", page_size=1)
        for idx, page in enumerate([page async for page in resp.iter_pages()]):
            total_result += 1
            assert page
            assert page.has_more == (idx + 1 < total)
            assert len(page.items) == size
            conversation = page.items[0]
            assert conversation.id == f"id_{idx + 1}"
        assert total_result == total

    async def test_async_conversations_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        conversation = make_conversation()
        respx_mock.get("/v1/conversation/retrieve").mock(httpx.Response(200, json={"data": conversation.model_dump()}))

        res = await coze.conversations.retrieve(conversation_id=conversation.id)
        assert res
        assert res.id == conversation.id
        assert res.last_section_id == conversation.last_section_id
