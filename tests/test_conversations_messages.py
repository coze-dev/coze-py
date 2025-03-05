import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Coze, Message, TokenAuth
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_create_conversations_messages(respx_mock, msg: Message) -> Message:
    msg._raw_response = httpx.Response(
        200,
        json={"data": msg.model_dump()},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.post("/v1/conversation/message/create").mock(msg._raw_response)
    return msg


def mock_retrieve_conversations_messages(respx_mock, msg: Message) -> Message:
    msg._raw_response = httpx.Response(
        200,
        json=msg.model_dump(),
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.get("/v1/conversation/message/retrieve").mock(msg._raw_response)
    return msg


def mock_update_conversations_messages(respx_mock, msg: Message) -> Message:
    msg._raw_response = httpx.Response(
        200,
        json=msg.model_dump(),
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.post("/v1/conversation/message/modify").mock(msg._raw_response)
    return msg


def mock_delete_conversations_messages(respx_mock, msg: Message) -> Message:
    msg._raw_response = httpx.Response(
        200,
        json=msg.model_dump(),
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.post("/v1/conversation/message/delete").mock(msg._raw_response)
    return msg


def mock_list_conversations_messages(respx_mock, total_count, page):
    logid = random_hex(10)
    respx_mock.post(
        "/v1/conversation/message/list",
        params={
            "conversation_id": "",
        },
        json={
            "order": "desc",
            "chat_id": None,
            "before_id": None,
            "after_id": None if page == 1 else f"id_{page - 1}",
            "limit": 1,
        },
    ).mock(
        httpx.Response(
            200,
            json={
                "first_id": "",
                "has_more": page < total_count,
                "last_id": f"id_{page}",
                "data": [Message.build_user_question_text(f"id_{page}").model_dump()],
            },
            headers={logid_key(): logid},
        )
    )
    return logid


@pytest.mark.respx(base_url="https://api.coze.com")
class TestConversationMessage:
    def test_sync_conversations_messages_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_msg = mock_create_conversations_messages(respx_mock, Message.build_assistant_answer("hi"))

        message = coze.conversations.messages.create(
            conversation_id="conversation id",
            role=mock_msg.role,
            content=mock_msg.content,
            content_type=mock_msg.content_type,
        )
        assert message
        assert message.response.logid == mock_msg.response.logid
        assert message.content == mock_msg.content

    def test_sync_conversations_messages_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        total = 10
        size = 1
        for idx in range(total):
            mock_list_conversations_messages(respx_mock, total_count=total, page=idx + 1)

        # no iter
        resp = coze.conversations.messages.list(conversation_id="", after_id="", limit=1)
        assert resp
        assert resp.has_more is True

        # iter dataset
        total_result = 0
        for message in resp:
            total_result += 1
            assert message
            assert message.content == f"id_{total_result}"
        assert total_result == total

        # iter page
        total_result = 0
        for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.has_more == (total_result < total)
            assert len(page.items) == size
            message = page.items[0]
            assert message.content == f"id_{total_result}"
        assert total_result == total

    def test_sync_conversations_messages_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_msg = mock_retrieve_conversations_messages(respx_mock, Message.build_user_question_text("hi"))

        message = coze.conversations.messages.retrieve(conversation_id="conversation id", message_id="message id")
        assert message
        assert message.response.logid == mock_msg.response.logid
        assert message.content == mock_msg.content

    def test_sync_conversations_messages_update(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_msg = mock_update_conversations_messages(respx_mock, Message.build_user_question_text("hi"))

        message = coze.conversations.messages.update(conversation_id="conversation id", message_id="message id")
        assert message
        assert message.response.logid == mock_msg.response.logid
        assert message.content == mock_msg.content

    def test_sync_conversations_messages_delete(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_msg = mock_delete_conversations_messages(respx_mock, Message.build_user_question_text("hi"))

        message = coze.conversations.messages.delete(conversation_id="conversation id", message_id="message id")
        assert message
        assert message.response.logid == mock_msg.response.logid
        assert message.content == mock_msg.content


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncConversationMessage:
    async def test_async_conversations_messages_create(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_msg = mock_create_conversations_messages(respx_mock, Message.build_assistant_answer("hi"))

        message = await coze.conversations.messages.create(
            conversation_id="conversation id",
            role=mock_msg.role,
            content=mock_msg.content,
            content_type=mock_msg.content_type,
        )
        assert message
        assert message.response.logid == mock_msg.response.logid
        assert message.content == mock_msg.content

    async def test_async_conversations_messages_list(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        total = 10
        size = 1
        for idx in range(total):
            mock_list_conversations_messages(respx_mock, total_count=total, page=idx + 1)

        # no iter
        resp = await coze.conversations.messages.list(conversation_id="", after_id="", limit=1)
        assert resp
        assert resp.has_more is True

        # iter dataset
        total_result = 0
        async for message in resp:
            total_result += 1
            assert message
            assert message.content == f"id_{total_result}"
        assert total_result == total

        # iter page
        total_result = 0
        async for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.has_more == (total_result < total)
            assert len(page.items) == size
            message = page.items[0]
            assert message.content == f"id_{total_result}"
        assert total_result == total

    async def test_async_conversations_messages_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_msg = mock_retrieve_conversations_messages(respx_mock, Message.build_user_question_text("hi"))

        message = await coze.conversations.messages.retrieve(conversation_id="conversation id", message_id="message id")
        assert message
        assert message.response.logid == mock_msg.response.logid
        assert message.content == mock_msg.content

    async def test_async_conversations_messages_update(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        mock_msg = mock_update_conversations_messages(respx_mock, Message.build_user_question_text("hi"))

        message = await coze.conversations.messages.update(conversation_id="conversation id", message_id="message id")
        assert message
        assert message.response.logid == mock_msg.response.logid
        assert message.content == mock_msg.content

    async def test_async_conversations_messages_delete(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_msg = mock_delete_conversations_messages(respx_mock, Message.build_user_question_text("hi"))

        message = await coze.conversations.messages.delete(conversation_id="conversation id", message_id="message id")
        assert message
        assert message.response.logid == mock_msg.response.logid
        assert message.content == mock_msg.content
