import base64

import httpx
import pytest

from cozepy import AsyncCoze, Chat, ChatEvent, ChatEventType, ChatStatus, Coze, MessageObjectString, TokenAuth
from cozepy.chat import ChatError, ChatUsage, Message
from cozepy.util import random_hex, write_pcm_to_wav_file
from tests.config import make_stream_response, read_file


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
    )


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

chat_failed_stream_testdata = make_stream_response("""
event:conversation.chat.failed
data:{"id":"7390342853760696354","conversation_id":"7390331532575195148","bot_id":"7374724495711502387","completed_at":1720698285,"failed_at":1720698286,"last_error":{"code":5000,"msg":"event interval error"},"status":"failed","usage":{"token_count":0,"output_count":0,"input_count":0}}
        """)

chat_error_stream_testdata = make_stream_response("""
event:error
data:{}
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
class TestChat:
    def test_sync_chat_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        respx_mock.post("/v3/chat").mock(
            httpx.Response(200, json={"data": make_chat(conversation_id, ChatStatus.FAILED).model_dump()})
        )
        res = coze.chat.create(bot_id="bot", user_id="user")

        assert res
        assert res.conversation_id == conversation_id

    def test_sync_chat_stream(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat").mock(chat_stream_testdata)
        events = list(coze.chat.stream(bot_id="bot", user_id="user"))

        assert events
        assert len(events) == 9
        assert events[0] == ChatEvent(
            logid="logid",
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

        chat_audio_stream_resp = make_stream_response(read_file("testdata/chat_audio_stream_resp.txt"))
        respx_mock.post("/v3/chat").mock(chat_audio_stream_resp)
        events = list(
            coze.chat.stream(
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
        )

        assert events
        assert len(events) == 7

        assert base64.b64decode(events[-1].message.content)
        write_pcm_to_wav_file(base64.b64decode(events[-1].message.content), f"{random_hex(10)}.wav")

    def test_sync_chat_stream_error(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat").mock(chat_error_stream_testdata)
        with pytest.raises(Exception, match="error event"):
            list(coze.chat.stream(bot_id="bot", user_id="user"))

    def test_sync_chat_stream_failed(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat").mock(chat_failed_stream_testdata)
        a = list(coze.chat.stream(bot_id="bot", user_id="user"))
        assert a[0].chat.last_error.code == 5000

    def test_chat_stream_invalid_event(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat").mock(
            make_stream_response("""
event:invalid
data:{}
        """)
        )
        with pytest.raises(Exception, match="invalid chat.event: invalid"):
            list(coze.chat.stream(bot_id="bot", user_id="user"))

    def test_chat_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        respx_mock.post("/v3/chat/retrieve").mock(
            httpx.Response(200, json={"data": make_chat(conversation_id, ChatStatus.FAILED).model_dump()})
        )
        res = coze.chat.retrieve(conversation_id="conversation", chat_id="chat")

        assert res
        assert res.conversation_id == conversation_id

    def test_submit_tool_outputs_not_stream(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        respx_mock.post("/v3/chat/submit_tool_outputs").mock(
            httpx.Response(200, json={"data": make_chat(conversation_id, ChatStatus.FAILED).model_dump()})
        )
        res = coze.chat.submit_tool_outputs(
            conversation_id="conversation", chat_id="chat", tool_outputs=[], stream=False
        )

        assert res
        assert res.conversation_id == conversation_id

    def test_sync_submit_tool_outputs_stream(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat/submit_tool_outputs").mock(chat_stream_testdata)
        events = list(
            coze.chat.submit_tool_outputs(conversation_id="conversation", chat_id="chat", tool_outputs=[], stream=True)
        )

        assert events
        assert len(events) == 9
        assert events[0] == ChatEvent(
            logid="logid",
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

    def test_cancel(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        respx_mock.post("/v3/chat/cancel").mock(
            httpx.Response(200, json={"data": make_chat(conversation_id, ChatStatus.FAILED).model_dump()})
        )
        res = coze.chat.cancel(conversation_id="conversation", chat_id="chat")

        assert res
        assert res.conversation_id == conversation_id

    def test_sync_chat_poll(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        respx_mock.post("/v3/chat").mock(
            httpx.Response(200, json={"data": make_chat(conversation_id, ChatStatus.IN_PROGRESS).model_dump()})
        )
        respx_mock.post("/v3/chat/retrieve").mock(
            httpx.Response(200, json={"data": make_chat(conversation_id, ChatStatus.COMPLETED).model_dump()})
        )
        msg = Message.build_user_question_text("hi")
        respx_mock.get("/v3/chat/message/list").mock(
            httpx.Response(
                200,
                json={"data": [msg.model_dump()]},
            )
        )

        res = coze.chat.create_and_poll(bot_id="bot", user_id="user")

        assert res
        assert res.chat.conversation_id == conversation_id
        assert res.messages
        assert res.messages[0].content == "hi"


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncChatConversationMessage:
    async def test_async_chat_create(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        respx_mock.post("/v3/chat").mock(
            httpx.Response(200, json={"data": make_chat(conversation_id, ChatStatus.FAILED).model_dump()})
        )
        res = await coze.chat.create(bot_id="bot", user_id="user")

        assert res
        assert res.conversation_id == conversation_id

    async def test_async_chat_stream(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat").mock(chat_stream_testdata)
        events = [event async for event in coze.chat.stream(bot_id="bot", user_id="user")]

        assert events
        assert len(events) == 9
        assert events[0] == ChatEvent(
            logid="logid",
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

    async def test_sync_chat_audio_stream(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        chat_audio_stream_resp = make_stream_response(read_file("testdata/chat_audio_stream_resp.txt"))
        respx_mock.post("/v3/chat").mock(chat_audio_stream_resp)
        events = [
            event
            async for event in coze.chat.stream(
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
        ]

        assert events
        assert len(events) == 7

        assert base64.b64decode(events[-1].message.content)
        write_pcm_to_wav_file(base64.b64decode(events[-1].message.content), f"{random_hex(10)}.wav")

    async def test_async_chat_stream_error(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat").mock(
            make_stream_response("""
event:error
data:{}
        """)
        )
        with pytest.raises(Exception, match="error event"):
            async for event in coze.chat.stream(bot_id="bot", user_id="user"):
                assert event

    async def test_async_chat_stream_invalid_event(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat").mock(
            make_stream_response("""
event:invalid
data:{}
        """)
        )
        with pytest.raises(Exception, match="invalid chat.event: invalid"):
            async for event in coze.chat.stream(bot_id="bot", user_id="user"):
                assert event

    async def test_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        respx_mock.post("/v3/chat/retrieve").mock(
            httpx.Response(200, json={"data": make_chat(conversation_id, ChatStatus.FAILED).model_dump()})
        )
        res = await coze.chat.retrieve(conversation_id="conversation", chat_id="chat")

        assert res
        assert res.conversation_id == conversation_id

    async def test_submit_tool_outputs_not_stream(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        respx_mock.post("/v3/chat/submit_tool_outputs").mock(
            httpx.Response(200, json={"data": make_chat(conversation_id, ChatStatus.FAILED).model_dump()})
        )
        res = await coze.chat.submit_tool_outputs(conversation_id="conversation", chat_id="chat", tool_outputs=[])

        assert res
        assert res.conversation_id == conversation_id

    async def test_async_submit_tool_outputs_stream(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat/submit_tool_outputs").mock(chat_stream_testdata)
        events = [
            i
            async for i in coze.chat.submit_tool_outputs_stream(
                conversation_id="conversation",
                chat_id="chat",
                tool_outputs=[],
            )
        ]

        assert events
        assert len(events) == 9
        assert events[0] == ChatEvent(
            logid="logid",
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

    async def test_chat_cancel(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        respx_mock.post("/v3/chat/cancel").mock(
            httpx.Response(200, json={"data": make_chat(conversation_id, ChatStatus.FAILED).model_dump()})
        )
        res = await coze.chat.cancel(conversation_id="conversation", chat_id="chat")

        assert res
        assert res.conversation_id == conversation_id
