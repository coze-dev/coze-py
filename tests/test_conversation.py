import httpx
import pytest

from cozepy import AsyncCoze, Conversation, Coze, TokenAuth


@pytest.mark.respx(base_url="https://api.coze.com")
class TestConversation:
    def test_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        conversation = Conversation(id="id", created_at=1, meta_data={})
        respx_mock.post("/v1/conversation/create").mock(httpx.Response(200, json={"data": conversation.model_dump()}))

        res = coze.conversations.create()
        assert res
        assert res.id == conversation.id

    def test_conversations_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        conversation = Conversation(id="id", created_at=1, meta_data={})
        respx_mock.get("/v1/conversation/retrieve").mock(httpx.Response(200, json={"data": conversation.model_dump()}))

        res = coze.conversations.retrieve(conversation_id="id")
        assert res
        assert res.id == conversation.id


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncConversation:
    async def test_conversation_create(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        conversation = Conversation(id="id", created_at=1, meta_data={})
        respx_mock.post("/v1/conversation/create").mock(httpx.Response(200, json={"data": conversation.model_dump()}))

        res = await coze.conversations.create()
        assert res
        assert res.id == conversation.id

    async def test_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        conversation = Conversation(id="id", created_at=1, meta_data={})
        respx_mock.get("/v1/conversation/retrieve").mock(httpx.Response(200, json={"data": conversation.model_dump()}))

        res = await coze.conversations.retrieve(conversation_id="id")
        assert res
        assert res.id == conversation.id
