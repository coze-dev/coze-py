import base64
import os
import tempfile

import httpx
import pytest

from cozepy import (
    AsyncCoze,
    Chat,
    ChatError,
    ChatEvent,
    ChatEventType,
    ChatStatus,
    ChatUsage,
    Coze,
    Message,
    MessageObjectString,
    TokenAuth,
)
from cozepy.util import random_hex, write_pcm_to_wav_file
from tests.test_util import logid_key, make_stream_response, read_file


def make_chat(conversation_id: str = "conversation_id", status: ChatStatus = ChatStatus.IN_PROGRESS) -> Chat:
    return Chat(
        id="id",
        conversation_id=conversation_id,
        bot_id="bot_id",
        created_at=123,
        completed_at=123,
        failed_at=123,
        meta_data={},
        status=status,
        logid=random_hex(10),
    )


def mock_chat_create(respx_mock, conversation_id: str, status: ChatStatus):
    logid = random_hex(10)
    respx_mock.post("/v3/chat").mock(
        httpx.Response(
            200, json={"data": make_chat(conversation_id, status).model_dump()}, headers={logid_key(): logid}
        )
    )
    return logid


def mock_chat_stream(respx_mock, content: str) -> str:
    logid = random_hex(10)
    respx_mock.post("/v3/chat").mock(
        httpx.Response(
            200,
            headers={"content-type": "text/event-stream", logid_key(): logid},
            content=content,
        )
    )
    return logid


def mock_chat_retrieve(respx_mock, conversation_id: str, status: ChatStatus):
    logid = random_hex(10)
    respx_mock.post("/v3/chat/retrieve").mock(
        httpx.Response(
            200,
            json={"data": make_chat(conversation_id, status).model_dump()},
            headers={logid_key(): logid},
        )
    )
    return logid


def mock_chat_submit_tool_outputs(respx_mock, conversation_id: str, status: ChatStatus):
    logid = random_hex(10)
    respx_mock.post("/v3/chat/submit_tool_outputs").mock(
        httpx.Response(
            200,
            json={"data": make_chat(conversation_id, status).model_dump()},
            headers={logid_key(): logid},
        )
    )
    return logid


def mock_chat_submit_tool_outputs_stream(respx_mock, content: str) -> str:
    logid = random_hex(10)
    respx_mock.post("/v3/chat/submit_tool_outputs").mock(
        httpx.Response(
            200,
            headers={"content-type": "text/event-stream", logid_key(): logid},
            content=content,
        )
    )
    return logid


def mock_chat_cancel(respx_mock, conversation_id: str, status: ChatStatus):
    logid = random_hex(10)
    respx_mock.post("/v3/chat/cancel").mock(
        httpx.Response(
            200, json={"data": make_chat(conversation_id, status).model_dump()}, headers={logid_key(): logid}
        )
    )
    return logid


def mock_chat_poll(
    respx_mock,
    conversation_id: str,
):
    respx_mock.post("/v3/chat").mock(
        httpx.Response(
            200,
            json={"data": make_chat(conversation_id, ChatStatus.IN_PROGRESS).model_dump()},
            headers={logid_key(): random_hex(10)},
        )
    )
    chat = make_chat(conversation_id, ChatStatus.COMPLETED)
    respx_mock.post("/v3/chat/retrieve").mock(
        httpx.Response(
            200,
            json={"data": chat.model_dump()},
            headers={logid_key(): chat.logid},
        )
    )
    msg = Message.build_user_question_text("hi")
    list_message_logid = random_hex(10)
    respx_mock.get("/v3/chat/message/list").mock(
        httpx.Response(
            200,
            json={"data": [msg.model_dump()]},
            headers={logid_key(): list_message_logid},
        )
    )
    return chat, list_message_logid


chat_stream_testdata = make_stream_response("""
event:conversation.chat.created
data:{"id":"7382159487131697202","conversation_id":"7381473525342978089","bot_id":"7379462189365198898","completed_at":1718792949,"last_error":{"code":0,"msg":""},"status":"created","usage":{"token_count":0,"output_count":0,"input_count":0}}

event:conversation.chat.in_progress
data:{"id":"7382159487131697202","conversation_id":"7381473525342978089","bot_id":"7379462189365198898","completed_at":1718792949,"last_error":{"code":0,"msg":""},"status":"in_progress","usage":{"token_count":0,"output_count":0,"input_count":0}}

event:conversation.message.delta
data:{"id":"7382159494123470858","conversation_id":"7381473525342978089","bot_id":"7379462189365198898","role":"assistant","type":"answer","content":"2","content_type":"text","chat_id":"7382159487131697202"}

event:conversation.message.delta
data:{"id":"7382159494123470858","conversation_id":"7381473525342978089","bot_id":"7379462189365198898","role":"assistant","type":"answer","content":"0","content_type":"text","chat_id":"7382159487131697202"}

event:conversation.message.delta
data:{"id":"7382159494123470858","conversation_id":"7381473525342978089","bot_id":"7379462189365198898","role":"assistant","type":"answer","content":"星期三","content_type":"text","chat_id":"7382159487131697202"}

event:conversation.message.delta
data:{"id":"7382159494123470858","conversation_id":"7381473525342978089","bot_id":"7379462189365198898","role":"assistant","type":"answer","content":"。","content_type":"text","chat_id":"7382159487131697202"}

event:conversation.message.completed
data:{"id":"7382159494123470858","conversation_id":"7381473525342978089","bot_id":"7379462189365198898","role":"assistant","type":"answer","content":"2024 年 10 月 1 日是星期三。","content_type":"text","chat_id":"7382159487131697202"}

event:conversation.message.completed
data:{"id":"7382159494123552778","conversation_id":"7381473525342978089","bot_id":"7379462189365198898","role":"assistant","type":"verbose","content":"{\\"msg_type\\":\\"generate_answer_finish\\",\\"data\\":\\"\\",\\"from_module\\":null,\\"from_unit\\":null}","content_type":"text","chat_id":"7382159487131697202"}

event:conversation.chat.completed
data:{"id":"7382159487131697202","conversation_id":"7381473525342978089","bot_id":"7379462189365198898","completed_at":1718792949,"last_error":{"code":0,"msg":""},"status":"completed","usage":{"token_count":633,"output_count":19,"input_count":614}}

event:done
data:"[DONE]"
        """)


class TestMessageObjectString:
    def test_build_image(self):
        with pytest.raises(ValueError, match="file_id or file_url must be specified"):
            MessageObjectString.build_image()

    def test_build_file(self):
        with pytest.raises(ValueError, match="file_id or file_url must be specified"):
            MessageObjectString.build_file()

    def test_build_audio(self):
        with pytest.raises(ValueError, match="file_id or file_url must be specified"):
            MessageObjectString.build_audio()


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncChat:
    def test_sync_chat_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        mock_logid = mock_chat_create(respx_mock, conversation_id, ChatStatus.FAILED)
        res = coze.chat.create(bot_id="bot", user_id="user")

        assert res
        assert res.logid is not None
        assert res.logid == mock_logid
        assert res.conversation_id == conversation_id

    def test_sync_chat_stream(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_chat_stream(respx_mock, read_file("testdata/chat_text_stream_resp.txt"))
        stream = coze.chat.stream(bot_id="bot", user_id="user")

        assert stream
        assert stream.logid is not None
        assert stream.logid == mock_logid

        events = list(stream)
        assert len(events) == 8
        assert events[0] == ChatEvent(
            logid=mock_logid,
            event=ChatEventType.CONVERSATION_CHAT_CREATED,
            chat=Chat(
                id="7382159487131697202",
                conversation_id="7381473525342978089",
                bot_id="7379462189365198898",
                created_at=None,
                completed_at=1718792949,
                failed_at=None,
                meta_data=None,
                last_error=ChatError(code=0, msg=""),
                status=ChatStatus.CREATED,
                required_action=None,
                usage=ChatUsage(token_count=0, output_count=0, input_count=0),
            ),
        )
        assert events[len(events) - 1].event == ChatEventType.CONVERSATION_CHAT_COMPLETED

    def test_sync_chat_audio_stream(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_chat_stream(respx_mock, read_file("testdata/chat_audio_stream_resp.txt"))
        stream = coze.chat.stream(
            bot_id="bot",
            user_id="user",
            additional_messages=[
                Message.build_user_question_objects(
                    [
                        MessageObjectString.build_audio(file_id="fake file id"),
                    ]
                ),
            ],
        )
        assert stream
        assert stream.logid is not None
        assert stream.logid == mock_logid

        events = list(stream)
        assert events
        assert len(events) == 7

        assert base64.b64decode(events[-1].message.content)
        temp_filename = f"{tempfile.mkdtemp()}/{random_hex(10)}.wav"
        write_pcm_to_wav_file(base64.b64decode(events[-1].message.content), temp_filename)
        assert os.path.exists(temp_filename)

    def test_sync_chat_stream_error(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_chat_stream(respx_mock, read_file("testdata/chat_error_resp.txt"))
        stream = coze.chat.stream(bot_id="bot", user_id="user")
        assert stream
        assert stream.logid is not None
        assert stream.logid == mock_logid

        with pytest.raises(Exception, match="error event"):
            list(stream)

    def test_sync_chat_stream_failed(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_chat_stream(respx_mock, read_file("testdata/chat_failed_resp.txt"))
        stream = coze.chat.stream(bot_id="bot", user_id="user")
        assert stream
        assert stream.logid is not None
        assert stream.logid == mock_logid

        events = list(stream)
        assert events
        assert len(events) == 1
        assert events[0].chat.last_error.code == 5000

    def test_sync_chat_stream_invalid_event(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_chat_stream(respx_mock, read_file("testdata/chat_invalid_resp.txt"))

        stream = coze.chat.stream(bot_id="bot", user_id="user")
        assert stream
        assert stream.logid is not None
        assert stream.logid == mock_logid

        with pytest.raises(Exception, match="invalid chat.event: invalid"):
            list(stream)

    def test_sync_chat_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        mock_logid = mock_chat_retrieve(respx_mock, conversation_id, ChatStatus.FAILED)
        res = coze.chat.retrieve(conversation_id=conversation_id, chat_id="chat")

        assert res
        assert res.logid is not None
        assert res.logid == mock_logid
        assert res.conversation_id == conversation_id

    def test_sync_submit_tool_outputs_not_stream(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        mock_logid = mock_chat_submit_tool_outputs(respx_mock, conversation_id, ChatStatus.FAILED)
        res = coze.chat.submit_tool_outputs(
            conversation_id=conversation_id, chat_id="chat", tool_outputs=[], stream=False
        )

        assert res
        assert res.logid is not None
        assert res.logid == mock_logid
        assert res.conversation_id == conversation_id

    def test_sync_submit_tool_outputs_stream(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_chat_submit_tool_outputs_stream(respx_mock, read_file("testdata/chat_text_stream_resp.txt"))
        stream = coze.chat.submit_tool_outputs(
            conversation_id="conversation", chat_id="chat", tool_outputs=[], stream=True
        )
        assert stream
        assert stream.logid is not None
        assert stream.logid == mock_logid

        events = list(stream)
        assert events
        assert len(events) == 8
        assert events[0] == ChatEvent(
            logid=mock_logid,
            event=ChatEventType.CONVERSATION_CHAT_CREATED,
            chat=Chat(
                id="7382159487131697202",
                conversation_id="7381473525342978089",
                bot_id="7379462189365198898",
                created_at=None,
                completed_at=1718792949,
                failed_at=None,
                meta_data=None,
                last_error=ChatError(code=0, msg=""),
                status=ChatStatus.CREATED,
                required_action=None,
                usage=ChatUsage(token_count=0, output_count=0, input_count=0),
            ),
        )
        assert events[len(events) - 1].event == ChatEventType.CONVERSATION_CHAT_COMPLETED

    def test_sync_chat_cancel(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        mock_logid = mock_chat_cancel(respx_mock, conversation_id, ChatStatus.FAILED)
        res = coze.chat.cancel(conversation_id="conversation", chat_id="chat")

        assert res
        assert res.logid is not None
        assert res.logid == mock_logid
        assert res.conversation_id == conversation_id

    def test_sync_chat_poll(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        mock_chat, mock_logid = mock_chat_poll(
            respx_mock,
            conversation_id,
        )

        res = coze.chat.create_and_poll(bot_id="bot", user_id="user")

        assert res
        assert res.chat.logid == mock_chat.logid
        assert res.chat.conversation_id == conversation_id
        assert res.messages
        assert res.messages[0].content == "hi"


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncChatConversationMessage:
    async def test_async_chat_create(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        mock_logid = mock_chat_create(respx_mock, conversation_id, ChatStatus.FAILED)
        res = await coze.chat.create(bot_id="bot", user_id="user")

        assert res
        assert res.logid is not None
        assert res.logid == mock_logid
        assert res.conversation_id == conversation_id

    async def test_async_chat_stream(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        mock_logid = mock_chat_stream(respx_mock, read_file("testdata/chat_text_stream_resp.txt"))
        stream = coze.chat.stream(bot_id="bot", user_id="user")
        events = [event async for event in stream]

        assert stream
        assert len(events) == 8
        assert events[0] == ChatEvent(
            logid=mock_logid,
            event=ChatEventType.CONVERSATION_CHAT_CREATED,
            chat=Chat(
                id="7382159487131697202",
                conversation_id="7381473525342978089",
                bot_id="7379462189365198898",
                created_at=None,
                completed_at=1718792949,
                failed_at=None,
                meta_data=None,
                last_error=ChatError(code=0, msg=""),
                status=ChatStatus.CREATED,
                required_action=None,
                usage=ChatUsage(token_count=0, output_count=0, input_count=0),
            ),
        )
        assert events[len(events) - 1].event == ChatEventType.CONVERSATION_CHAT_COMPLETED

    async def test_async_chat_audio_stream(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        mock_logid = mock_chat_stream(respx_mock, read_file("testdata/chat_audio_stream_resp.txt"))  # noqa: F841
        stream = coze.chat.stream(
            bot_id="bot",
            user_id="user",
            additional_messages=[
                Message.build_user_question_objects(
                    [
                        MessageObjectString.build_audio(file_id="fake file id"),
                    ]
                ),
            ],
        )
        assert stream
        events = [event async for event in stream]
        assert events
        assert len(events) == 7

        assert base64.b64decode(events[-1].message.content)
        temp_filename = f"{tempfile.mkdtemp()}/{random_hex(10)}.wav"
        write_pcm_to_wav_file(base64.b64decode(events[-1].message.content), temp_filename)
        assert os.path.exists(temp_filename)

    async def test_async_chat_stream_error(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        mock_logid = mock_chat_stream(respx_mock, read_file("testdata/chat_error_resp.txt"))  # noqa: F841
        stream = coze.chat.stream(bot_id="bot", user_id="user")
        assert stream
        with pytest.raises(Exception, match="error event"):
            [event async for event in stream]

    async def test_async_chat_stream_failed(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        mock_logid = mock_chat_stream(respx_mock, read_file("testdata/chat_failed_resp.txt"))  # noqa: F841
        stream = coze.chat.stream(bot_id="bot", user_id="user")
        assert stream
        events = [event async for event in stream]
        assert events
        assert len(events) == 1
        assert events[0].chat.last_error.code == 5000

    async def test_async_chat_stream_invalid_event(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        mock_logid = mock_chat_stream(respx_mock, read_file("testdata/chat_invalid_resp.txt"))  # noqa: F841

        stream = coze.chat.stream(bot_id="bot", user_id="user")
        assert stream
        with pytest.raises(Exception, match="invalid chat.event: invalid"):
            [event async for event in stream]

    async def test_async_chat_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        mock_logid = mock_chat_retrieve(respx_mock, conversation_id, ChatStatus.FAILED)
        res = await coze.chat.retrieve(conversation_id=conversation_id, chat_id="chat")

        assert res
        assert res.logid is not None
        assert res.logid == mock_logid
        assert res.conversation_id == conversation_id

    async def test_async_submit_tool_outputs_not_stream(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        mock_logid = mock_chat_submit_tool_outputs(respx_mock, conversation_id, ChatStatus.FAILED)
        res = await coze.chat.submit_tool_outputs(conversation_id=conversation_id, chat_id="chat", tool_outputs=[])

        assert res
        assert res.logid is not None
        assert res.logid == mock_logid
        assert res.conversation_id == conversation_id

    async def test_async_submit_tool_outputs_stream(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        mock_logid = mock_chat_submit_tool_outputs_stream(respx_mock, read_file("testdata/chat_text_stream_resp.txt"))
        stream = coze.chat.submit_tool_outputs_stream(conversation_id="conversation", chat_id="chat", tool_outputs=[])
        assert stream
        events = [event async for event in stream]
        assert events
        assert len(events) == 8
        assert events[0] == ChatEvent(
            logid=mock_logid,
            event=ChatEventType.CONVERSATION_CHAT_CREATED,
            chat=Chat(
                id="7382159487131697202",
                conversation_id="7381473525342978089",
                bot_id="7379462189365198898",
                created_at=None,
                completed_at=1718792949,
                failed_at=None,
                meta_data=None,
                last_error=ChatError(code=0, msg=""),
                status=ChatStatus.CREATED,
                required_action=None,
                usage=ChatUsage(token_count=0, output_count=0, input_count=0),
            ),
        )
        assert events[len(events) - 1].event == ChatEventType.CONVERSATION_CHAT_COMPLETED

    async def test_async_chat_cancel(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        mock_logid = mock_chat_cancel(respx_mock, conversation_id, ChatStatus.FAILED)
        res = await coze.chat.cancel(conversation_id="conversation", chat_id="chat")

        assert res
        assert res.logid is not None
        assert res.logid == mock_logid
        assert res.conversation_id == conversation_id
