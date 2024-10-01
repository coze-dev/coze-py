import httpx
import pytest

from cozepy import Coze, Message, TokenAuth


@pytest.mark.respx(base_url="https://api.coze.com")
class TestChatMessage:
    def test_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        msg = Message.user_text_message("hi")
        msg2 = Message.user_text_message("hey")
        respx_mock.post("/v3/chat/message/list").mock(
            httpx.Response(
                200,
                json={"data": [msg.model_dump(), msg2.model_dump()]},
            )
        )

        message_list = coze.chat.messages.list(conversation_id="conversation id", chat_id="chat id")
        assert message_list
        assert message_list[0].content == msg.content
