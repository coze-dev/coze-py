import time

import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Conversation, Coze, Section, TokenAuth
from cozepy.util import random_hex
from tests.test_util import logid_key


def make_conversation() -> Conversation:
    return Conversation(
        id=random_hex(10),
        created_at=int(time.time()),
        meta_data={},
        last_section_id=random_hex(10),
    )


def make_section(conversation_id: str) -> Section:
    return Section(id=random_hex(10), conversation_id=conversation_id)


def mock_create_conversations(respx_mock) -> Conversation:
    conversation = make_conversation()
    conversation._raw_response = httpx.Response(
        200,
        json={"data": conversation.model_dump()},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.post("/v1/conversation/create").mock(conversation._raw_response)
    return conversation


def mock_list_conversations(respx_mock, total_count, page):
    respx_mock.get(
        "https://api.coze.com/v1/conversations",
        params={
            "page_num": page,
        },
    ).mock(
        httpx.Response(
            200,
            headers={logid_key(): "logid"},
            json={
                "data": {
                    "conversations": [
                        Conversation(
                            id=f"id_{page}", created_at=int(time.time()), meta_data={}, last_section_id=random_hex(10)
                        ).model_dump()
                    ],
                    "has_more": page < total_count,
                }
            },
        )
    )


def mock_retrieve_conversation(respx_mock) -> Conversation:
    conversation = make_conversation()
    conversation._raw_response = httpx.Response(
        200,
        json={"data": conversation.model_dump()},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.get("/v1/conversation/retrieve").mock(conversation._raw_response)
    return conversation


def mock_clear_conversation(respx_mock) -> Section:
    conversation = make_conversation()
    section = make_section(conversation.id)
    section._raw_response = httpx.Response(
        200,
        json={"data": section.model_dump()},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.post(f"/v1/conversations/{conversation.id}/clear").mock(section._raw_response)
    return section


def mock_update_conversation(respx_mock) -> Conversation:
    conversation = make_conversation()
    conversation.name = "updated_conversation_name"
    conversation.updated_at = int(time.time())
    conversation._raw_response = httpx.Response(
        200,
        json={"data": conversation.model_dump()},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.put(f"/v1/conversations/{conversation.id}").mock(conversation._raw_response)
    return conversation


def mock_delete_conversation(respx_mock, conversation_id: str):
    from cozepy.conversations import DeleteConversationResp

    resp = DeleteConversationResp()
    resp._raw_response = httpx.Response(
        200,
        json={"data": {}},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.delete(f"/v1/conversations/{conversation_id}").mock(resp._raw_response)
    return resp


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncConversation:
    def test_sync_conversations_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        bot_id = random_hex(10)
        mock_conversation = mock_create_conversations(respx_mock)

        res = coze.conversations.create(bot_id=bot_id)
        assert res
        assert res.response.logid == mock_conversation.response.logid
        assert res.id == mock_conversation.id
        assert res.last_section_id == mock_conversation.last_section_id

    def test_sync_conversations_create_with_name_and_connector(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        bot_id = random_hex(10)
        name = "测试会话名称"
        connector_id = "1024"
        mock_conversation = mock_create_conversations(respx_mock)

        res = coze.conversations.create(bot_id=bot_id, name=name, connector_id=connector_id)
        assert res
        assert res.response.logid == mock_conversation.response.logid
        assert res.id == mock_conversation.id
        assert res.last_section_id == mock_conversation.last_section_id

    def test_sync_conversations_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        total = 10
        size = 1
        for idx in range(total):
            mock_list_conversations(respx_mock, total, page=idx + 1)

        # no iter
        resp = coze.conversations.list(bot_id="bot id", page_size=1)
        assert resp
        assert resp.has_more is True

        # iter conversation
        total_result = 0
        for conversation in resp:
            total_result += 1
            assert conversation
            assert conversation.id == f"id_{total_result}"
        assert total_result == total

        # iter page
        total_result = 0
        for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.has_more == (total_result < total)
            assert len(page.items) == size
            conversation = page.items[0]
            assert conversation.id == f"id_{total_result}"
        assert total_result == total

    def test_sync_conversations_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_conversation = mock_retrieve_conversation(respx_mock)

        res = coze.conversations.retrieve(conversation_id=mock_conversation.id)
        assert res
        assert res.response.logid == mock_conversation.response.logid
        assert res.id == mock_conversation.id
        assert res.last_section_id == mock_conversation.last_section_id

    def test_sync_conversations_clear(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_section = mock_clear_conversation(respx_mock)

        res = coze.conversations.clear(conversation_id=mock_section.conversation_id)
        assert res
        assert res.response.logid == mock_section.response.logid
        assert res.id == mock_section.id
        assert res.conversation_id == mock_section.conversation_id

    def test_sync_conversations_update(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_conversation = mock_update_conversation(respx_mock)

        res = coze.conversations.update(conversation_id=mock_conversation.id, name="updated_conversation_name")
        assert res
        assert res.response.logid == mock_conversation.response.logid
        assert res.id == mock_conversation.id
        assert res.name == mock_conversation.name
        assert res.updated_at == mock_conversation.updated_at

    def test_sync_conversations_delete(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        conversation_id = random_hex(10)
        mock_resp = mock_delete_conversation(respx_mock, conversation_id)

        res = coze.conversations.delete(conversation_id=conversation_id)
        assert res
        assert res.response.logid == mock_resp.response.logid


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncConversation:
    async def test_async_conversations_create(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        bot_id = random_hex(10)
        mock_conversation = mock_create_conversations(respx_mock)

        res = await coze.conversations.create(bot_id=bot_id)
        assert res
        assert res.response.logid == mock_conversation.response.logid
        assert res.id == mock_conversation.id
        assert res.last_section_id == mock_conversation.last_section_id

    async def test_async_conversations_create_with_name_and_connector(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        bot_id = random_hex(10)
        name = "测试会话名称"
        connector_id = "1024"
        mock_conversation = mock_create_conversations(respx_mock)

        res = await coze.conversations.create(bot_id=bot_id, name=name, connector_id=connector_id)
        assert res
        assert res.response.logid == mock_conversation.response.logid
        assert res.id == mock_conversation.id
        assert res.last_section_id == mock_conversation.last_section_id

    async def test_async_conversations_list(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        total = 10
        size = 1
        for idx in range(total):
            mock_list_conversations(respx_mock, total, page=idx + 1)

        # no iter
        resp = await coze.conversations.list(bot_id="bot id", page_size=1)
        assert resp
        assert resp.has_more is True

        # iter conversation
        total_result = 0
        async for conversation in resp:
            total_result += 1
            assert conversation
            assert conversation.id == f"id_{total_result}"
        assert total_result == total

        # iter page
        total_result = 0
        async for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.has_more == (total_result < total)
            assert len(page.items) == size
            conversation = page.items[0]
            assert conversation.id == f"id_{total_result}"
        assert total_result == total

    async def test_async_conversations_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_conversation = mock_retrieve_conversation(respx_mock)

        res = await coze.conversations.retrieve(conversation_id=mock_conversation.id)
        assert res
        assert res.response.logid == mock_conversation.response.logid
        assert res.id == mock_conversation.id
        assert res.last_section_id == mock_conversation.last_section_id

    async def test_async_conversations_clear(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_section = mock_clear_conversation(respx_mock)

        res = await coze.conversations.clear(conversation_id=mock_section.conversation_id)
        assert res
        assert res.response.logid == mock_section.response.logid
        assert res.id == mock_section.id
        assert res.conversation_id == mock_section.conversation_id

    async def test_async_conversations_update(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_conversation = mock_update_conversation(respx_mock)

        res = await coze.conversations.update(conversation_id=mock_conversation.id, name="updated_conversation_name")
        assert res
        assert res.response.logid == mock_conversation.response.logid
        assert res.id == mock_conversation.id
        assert res.name == mock_conversation.name
        assert res.updated_at == mock_conversation.updated_at

    async def test_async_conversations_delete(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        conversation_id = random_hex(10)
        mock_resp = mock_delete_conversation(respx_mock, conversation_id)

        res = await coze.conversations.delete(conversation_id=conversation_id)
        assert res
        assert res.response.logid == mock_resp.response.logid
