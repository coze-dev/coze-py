import httpx
import pytest

from cozepy import AsyncCoze, Chat, ChatEvent, ChatEventType, ChatStatus, Coze, TokenAuth

chat_testdata = Chat(
    id="id",
    conversation_id="conversation_id",
    bot_id="bot_id",
    created_at=123,
    completed_at=123,
    failed_at=123,
    meta_data={},
    status=ChatStatus.FAILED,
)

chat_stream_testdata = """
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
        """


@pytest.mark.respx(base_url="https://api.coze.com")
class TestChat:
    def test_chat_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat").mock(httpx.Response(200, json={"data": chat_testdata.model_dump()}))
        res = coze.chat.create(bot_id="bot", user_id="user")

        assert res
        assert res.conversation_id == chat_testdata.conversation_id

    def test_chat_stream(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat").mock(httpx.Response(200, content=chat_stream_testdata))
        events = list(coze.chat.stream(bot_id="bot", user_id="user"))

        assert events
        assert len(events) == 9
        assert events[0] == ChatEvent(
            event=ChatEventType.CONVERSATION_CHAT_CREATED,
            chat=Chat(
                id="7382159487131697202",
                conversation_id="7381473525342978089",
                bot_id="7379462189365198898",
                created_at=None,
                completed_at=1718792949,
                failed_at=None,
                meta_data=None,
                status=ChatStatus.CREATED,
            ),
        )
        assert events[len(events) - 1].event == ChatEventType.CONVERSATION_CHAT_COMPLETED

    def test_chat_stream_error(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat").mock(
            httpx.Response(
                200,
                content="""
event:error
data:{}
        """,
            )
        )
        with pytest.raises(Exception, match="error event"):
            list(coze.chat.stream(bot_id="bot", user_id="user"))

    def test_chat_stream_invalid_event(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat").mock(
            httpx.Response(
                200,
                content="""
event:invalid
data:{}
        """,
            )
        )
        with pytest.raises(Exception, match="invalid chat.event: invalid"):
            list(coze.chat.stream(bot_id="bot", user_id="user"))

    def test_chat_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat/retrieve").mock(httpx.Response(200, json={"data": chat_testdata.model_dump()}))
        res = coze.chat.retrieve(conversation_id="conversation", chat_id="chat")

        assert res
        assert res.conversation_id == chat_testdata.conversation_id

    def test_submit_tool_outputs_not_stream(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat/submit_tool_outputs").mock(
            httpx.Response(200, json={"data": chat_testdata.model_dump()})
        )
        res = coze.chat.submit_tool_outputs(
            conversation_id="conversation", chat_id="chat", tool_outputs=[], stream=False
        )

        assert res
        assert res.conversation_id == chat_testdata.conversation_id

    def test_sync_submit_tool_outputs_stream(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat/submit_tool_outputs").mock(httpx.Response(200, content=chat_stream_testdata))
        events = list(
            coze.chat.submit_tool_outputs(conversation_id="conversation", chat_id="chat", tool_outputs=[], stream=True)
        )

        assert events
        assert len(events) == 9
        assert events[0] == ChatEvent(
            event=ChatEventType.CONVERSATION_CHAT_CREATED,
            chat=Chat(
                id="7382159487131697202",
                conversation_id="7381473525342978089",
                bot_id="7379462189365198898",
                created_at=None,
                completed_at=1718792949,
                failed_at=None,
                meta_data=None,
                status=ChatStatus.CREATED,
            ),
        )
        assert events[len(events) - 1].event == ChatEventType.CONVERSATION_CHAT_COMPLETED

    def test_cancel(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat/cancel").mock(httpx.Response(200, json={"data": chat_testdata.model_dump()}))
        res = coze.chat.cancel(conversation_id="conversation", chat_id="chat")

        assert res
        assert res.conversation_id == chat_testdata.conversation_id


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncChatConversationMessage:
    async def test_create(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat").mock(httpx.Response(200, json={"data": chat_testdata.model_dump()}))
        res = await coze.chat.create(bot_id="bot", user_id="user")

        assert res
        assert res.conversation_id == chat_testdata.conversation_id

    async def test_stream(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat").mock(httpx.Response(200, content=chat_stream_testdata))
        events = [event async for event in coze.chat.stream(bot_id="bot", user_id="user")]

        assert events
        assert len(events) == 9
        assert events[0] == ChatEvent(
            event=ChatEventType.CONVERSATION_CHAT_CREATED,
            chat=Chat(
                id="7382159487131697202",
                conversation_id="7381473525342978089",
                bot_id="7379462189365198898",
                created_at=None,
                completed_at=1718792949,
                failed_at=None,
                meta_data=None,
                status=ChatStatus.CREATED,
            ),
        )
        assert events[len(events) - 1].event == ChatEventType.CONVERSATION_CHAT_COMPLETED

    async def test_stream_error(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat").mock(
            httpx.Response(
                200,
                content="""
event:error
data:{}
        """,
            )
        )
        with pytest.raises(Exception, match="error event"):
            async for event in coze.chat.stream(bot_id="bot", user_id="user"):
                assert event

    async def test_stream_invalid_event(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat").mock(
            httpx.Response(
                200,
                content="""
event:invalid
data:{}
        """,
            )
        )
        with pytest.raises(Exception, match="invalid chat.event: invalid"):
            async for event in coze.chat.stream(bot_id="bot", user_id="user"):
                assert event

    async def test_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat/retrieve").mock(httpx.Response(200, json={"data": chat_testdata.model_dump()}))
        res = await coze.chat.retrieve(conversation_id="conversation", chat_id="chat")

        assert res
        assert res.conversation_id == chat_testdata.conversation_id

    async def test_submit_tool_outputs_not_stream(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat/submit_tool_outputs").mock(
            httpx.Response(200, json={"data": chat_testdata.model_dump()})
        )
        res = await coze.chat.submit_tool_outputs(conversation_id="conversation", chat_id="chat", tool_outputs=[])

        assert res
        assert res.conversation_id == chat_testdata.conversation_id

    async def test_async_submit_tool_outputs_stream(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat/submit_tool_outputs").mock(httpx.Response(200, content=chat_stream_testdata))
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
            event=ChatEventType.CONVERSATION_CHAT_CREATED,
            chat=Chat(
                id="7382159487131697202",
                conversation_id="7381473525342978089",
                bot_id="7379462189365198898",
                created_at=None,
                completed_at=1718792949,
                failed_at=None,
                meta_data=None,
                status=ChatStatus.CREATED,
            ),
        )
        assert events[len(events) - 1].event == ChatEventType.CONVERSATION_CHAT_COMPLETED

    async def test_chat_cancel(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v3/chat/cancel").mock(httpx.Response(200, json={"data": chat_testdata.model_dump()}))
        res = await coze.chat.cancel(conversation_id="conversation", chat_id="chat")

        assert res
        assert res.conversation_id == chat_testdata.conversation_id
