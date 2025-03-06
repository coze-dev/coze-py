import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Coze, Message, TokenAuth
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_chat_messages_list(respx_mock):
    logid = random_hex(10)
    msg = Message.build_user_question_text("hi")
    msg2 = Message.build_user_question_text("hey")
    respx_mock.get("/v3/chat/message/list").mock(
        httpx.Response(
            200,
            json={"data": [msg.model_dump(), msg2.model_dump()]},
            headers={logid_key(): logid},
        )
    )
    return msg, msg2, logid


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncChatMessages:
    def test_sync_chat_messages_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        msg, msg2, logid = mock_chat_messages_list(respx_mock)

        res = coze.chat.messages.list(conversation_id="conversation id", chat_id="chat id")
        assert res
        assert res.response.logid is not None
        assert res.response.logid == logid
        assert res[0].content == msg.content
        assert res[1].content == msg2.content


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncChatMessages:
    async def test_async_chat_messages_list(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        msg, msg2, logid = mock_chat_messages_list(respx_mock)

        res = await coze.chat.messages.list(conversation_id="conversation id", chat_id="chat id")
        assert res
        assert res.response.logid is not None
        assert res.response.logid == logid
        assert res[0].content == msg.content
        assert res[1].content == msg2.content
