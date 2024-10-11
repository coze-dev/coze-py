import httpx
import pytest

from cozepy import AsyncCoze, Coze, Message, TokenAuth


def mock_conversations_messages_list(respx_mock, has_more, last_id):
    respx_mock.post(
        "/v1/conversation/message/list",
        json={
            "order": "desc",
            "chat_id": None,
            "before_id": None,
            "after_id": f"{last_id}",
            "limit": 1,
        },
    ).mock(
        httpx.Response(
            200,
            json={
                "first_id": "",
                "has_more": has_more,
                "last_id": f"{last_id + 1}",
                "data": [Message.user_text_message(f"id_{last_id}").model_dump()],
            },
        )
    )


@pytest.mark.respx(base_url="https://api.coze.com")
class TestConversationMessage:
    def test_sync_conversations_messages_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        msg = Message.assistant_text_message("hi")
        respx_mock.post("/v1/conversation/message/create").mock(httpx.Response(200, json={"data": msg.model_dump()}))

        message = coze.conversations.messages.create(
            conversation_id="conversation id", role=msg.role, content=msg.content, content_type=msg.content_type
        )
        assert message
        assert message.content == msg.content

    def test_sync_conversations_messages_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_conversations_messages_list(respx_mock, has_more=True, last_id=1)

        page = coze.conversations.messages.list(conversation_id="conversation id", after_id="1", limit=1)
        assert page
        assert len(page.items) == 1

    def test_sync_conversations_messages_iterator(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        total = 10
        for idx in range(total):
            mock_conversations_messages_list(respx_mock, has_more=idx < total - 1, last_id=idx + 1)

        total_result = 0
        page = coze.conversations.messages.list(conversation_id="conversation id", before_id="", after_id="1", limit=1)
        for message in page:
            total_result += 1
            assert message
            assert message.content == f"id_{total_result}"
        assert total_result == total

    def test_sync_conversations_messages_page_iterator(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        total = 10
        for idx in range(total):
            mock_conversations_messages_list(respx_mock, has_more=idx < total - 1, last_id=idx + 1)

        total_result = 0
        page_iter = coze.conversations.messages.list(
            conversation_id="conversation id", before_id="", after_id="1", limit=1
        )
        for page in page_iter.iter_pages():
            total_result += 1
            assert page
            assert len(page.items) == 1
            message = page.items[0]
            assert message.content == f"id_{total_result}"
        assert total_result == total

    def test_sync_conversations_messages_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        msg = Message.user_text_message("hi")
        respx_mock.get("/v1/conversation/message/retrieve").mock(httpx.Response(200, json=msg.model_dump()))

        message = coze.conversations.messages.retrieve(conversation_id="conversation id", message_id="message id")
        assert message
        assert message.content == msg.content

    def test_sync_conversations_messages_update(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        msg = Message.user_text_message("hi")
        respx_mock.post("/v1/conversation/message/modify").mock(httpx.Response(200, json=msg.model_dump()))

        message = coze.conversations.messages.update(conversation_id="conversation id", message_id="message id")
        assert message
        assert message.content == msg.content

    def test_sync_conversations_messages_delete(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        msg = Message.user_text_message("hi")
        respx_mock.post("/v1/conversation/message/delete").mock(httpx.Response(200, json=msg.model_dump()))

        message = coze.conversations.messages.delete(conversation_id="conversation id", message_id="message id")
        assert message
        assert message.content == msg.content


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncConversationMessage:
    async def test_async_conversations_messages_create(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        msg = Message.assistant_text_message("hi")
        respx_mock.post("/v1/conversation/message/create").mock(httpx.Response(200, json={"data": msg.model_dump()}))

        message = await coze.conversations.messages.create(
            conversation_id="conversation id", role=msg.role, content=msg.content, content_type=msg.content_type
        )
        assert message
        assert message.content == msg.content

    async def test_async_conversations_messages_list(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        mock_conversations_messages_list(respx_mock, has_more=True, last_id=1)

        page = await coze.conversations.messages.list(conversation_id="conversation id", after_id="1", limit=1)
        assert page
        assert len(page.items) == 1

    async def test_async_conversations_messages_iterator(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        total = 10
        for idx in range(total):
            mock_conversations_messages_list(respx_mock, has_more=idx < total - 1, last_id=idx + 1)

        total_result = 0
        page = await coze.conversations.messages.list(conversation_id="conversation id", after_id="1", limit=1)
        async for message in page:
            total_result += 1
            assert message
            assert message.content == f"id_{total_result}"
        assert total_result == total

    async def test_async_conversations_messages_page_iterator(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        total = 10
        for idx in range(total):
            mock_conversations_messages_list(respx_mock, has_more=idx < total - 1, last_id=idx + 1)

        total_result = 0
        page_iter = await coze.conversations.messages.list(
            conversation_id="conversation id", before_id="", after_id="1", limit=1
        )
        async for page in page_iter.iter_pages():
            total_result += 1
            assert page
            assert len(page.items) == 1
            message = page.items[0]
            assert message.content == f"id_{total_result}"
        assert total_result == total

    async def test_async_conversations_messages_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        msg = Message.user_text_message("hi")
        respx_mock.get("/v1/conversation/message/retrieve").mock(httpx.Response(200, json=msg.model_dump()))

        message = await coze.conversations.messages.retrieve(conversation_id="conversation id", message_id="message id")
        assert message
        assert message.content == msg.content

    async def test_async_conversations_messages_update(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        msg = Message.user_text_message("hi")
        respx_mock.post("/v1/conversation/message/modify").mock(httpx.Response(200, json=msg.model_dump()))

        message = await coze.conversations.messages.update(conversation_id="conversation id", message_id="message id")
        assert message
        assert message.content == msg.content

    async def test_async_conversations_messages_delete(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        msg = Message.user_text_message("hi")
        respx_mock.post("/v1/conversation/message/delete").mock(httpx.Response(200, json=msg.model_dump()))

        message = await coze.conversations.messages.delete(conversation_id="conversation id", message_id="message id")
        assert message
        assert message.content == msg.content
