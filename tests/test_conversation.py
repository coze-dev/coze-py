import time

import httpx
import pytest

from cozepy import AsyncCoze, Conversation, Coze, TokenAuth
from cozepy.util import random_hex


def make_conversation():
    return Conversation(id=random_hex(10), created_at=int(time.time()), meta_data={}, last_section_id=random_hex(10))


@pytest.mark.respx(base_url="https://api.coze.com")
class TestConversation:
    def test_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        conversation = make_conversation()
        respx_mock.post("/v1/conversation/create").mock(httpx.Response(200, json={"data": conversation.model_dump()}))

        res = coze.conversations.create()
        assert res
        assert res.id == conversation.id
        assert res.last_section_id == conversation.last_section_id

    def test_conversations_retrieve(self, respx_mock):
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
    async def test_conversation_create(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        conversation = make_conversation()
        respx_mock.post("/v1/conversation/create").mock(httpx.Response(200, json={"data": conversation.model_dump()}))

        res = await coze.conversations.create()
        assert res
        assert res.id == conversation.id
        assert res.last_section_id == conversation.last_section_id

    async def test_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        conversation = make_conversation()
        respx_mock.get("/v1/conversation/retrieve").mock(httpx.Response(200, json={"data": conversation.model_dump()}))

        res = await coze.conversations.retrieve(conversation_id=conversation.id)
        assert res
        assert res.id == conversation.id
        assert res.last_section_id == conversation.last_section_id
