import httpx
import pytest

from cozepy import Coze, Message, TokenAuth


@pytest.mark.respx(base_url="https://api.coze.com")
class TestConversationMessage:
    def test_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        msg = Message.user_text_message("hi")
        respx_mock.post("/v1/conversation/message/create").mock(httpx.Response(200, json={"data": msg.model_dump()}))

        message = coze.conversations.messages.create(
            conversation_id="conversation id", role=msg.role, content=msg.content, content_type=msg.content_type
        )
        assert message
        assert message.content == msg.content

    def test_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        msg = Message.user_text_message("hi")
        respx_mock.post("/v1/conversation/message/list").mock(
            httpx.Response(
                200, json={"first_id": "first_id", "has_more": False, "last_id": "last_id", "data": [msg.model_dump()]}
            )
        )

        message_list = coze.conversations.messages.list(conversation_id="conversation id")
        assert message_list
        assert len(message_list.items) == 1

    def test_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        msg = Message.user_text_message("hi")
        respx_mock.get("/v1/conversation/message/retrieve").mock(httpx.Response(200, json=msg.model_dump()))

        message = coze.conversations.messages.retrieve(conversation_id="conversation id", message_id="message id")
        assert message
        assert message.content == msg.content

    def test_update(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        msg = Message.user_text_message("hi")
        respx_mock.post("/v1/conversation/message/modify").mock(httpx.Response(200, json=msg.model_dump()))

        message = coze.conversations.messages.update(conversation_id="conversation id", message_id="message id")
        assert message
        assert message.content == msg.content

    def test_delete(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        msg = Message.user_text_message("hi")
        respx_mock.post("/v1/conversation/message/delete").mock(httpx.Response(200, json=msg.model_dump()))

        message = coze.conversations.messages.delete(conversation_id="conversation id", message_id="message id")
        assert message
        assert message.content == msg.content
