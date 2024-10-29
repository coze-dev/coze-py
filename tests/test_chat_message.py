import httpx
import pytest

from cozepy import AsyncCoze, Coze, Message, TokenAuth


@pytest.mark.respx(base_url="https://api.coze.com")
class TestChatMessage:
    def test_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        msg = Message.build_user_question_text("hi")
        msg2 = Message.build_user_question_text("hey")
        respx_mock.get("/v3/chat/message/list").mock(
            httpx.Response(
                200,
                json={"data": [msg.model_dump(), msg2.model_dump()]},
            )
        )

        message_list = coze.chat.messages.list(conversation_id="conversation id", chat_id="chat id")
        assert message_list
        assert message_list[0].content == msg.content


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncChatMessage:
    async def test_chat_message_list(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        msg = Message.build_user_question_text("hi")
        msg2 = Message.build_user_question_text("hey")
        respx_mock.get("/v3/chat/message/list").mock(
            httpx.Response(
                200,
                json={"data": [msg.model_dump(), msg2.model_dump()]},
            )
        )

        message_list = await coze.chat.messages.list(conversation_id="conversation id", chat_id="chat id")
        assert message_list
        assert message_list[0].content == msg.content
