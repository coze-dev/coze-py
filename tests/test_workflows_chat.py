import httpx
import pytest

from cozepy import (
    AsyncCoze,
    AsyncTokenAuth,
    Chat,
    ChatError,
    ChatEvent,
    ChatEventType,
    ChatStatus,
    ChatUsage,
    Coze,
    CozeAPIError,
    TokenAuth,
)
from cozepy.util import random_hex
from tests.test_util import logid_key, read_file


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


def mock_workflows_chat_stream(respx_mock, content: str) -> str:
    logid = random_hex(10)
    respx_mock.post("/v1/workflows/chat").mock(
        httpx.Response(
            200,
            headers={"content-type": "text/event-stream", logid_key(): logid},
            content=content,
        )
    )
    return logid


def mock_workflows_chat_stream_json_fail(respx_mock) -> str:
    logid = random_hex(10)
    respx_mock.post("/v1/workflows/chat").mock(
        httpx.Response(
            200,
            headers={"content-type": "application/json", logid_key(): logid},
            content='{"code":4000,"msg":"json fail"}',
        )
    )
    return logid


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncWorkflowsChat:
    def test_sync_workflows_chat_stream(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_workflows_chat_stream(respx_mock, read_file("testdata/workflows_chat_stream_resp.txt"))
        stream = coze.workflows.chat.stream(workflow_id="workflow", bot_id="bot")

        assert stream
        assert stream.response.logid == mock_logid

        events = list(stream)
        assert len(events) == 8
        assert (
            events[0].model_dump()
            == ChatEvent(
                event=ChatEventType.CONVERSATION_CHAT_CREATED,
                chat=Chat(
                    id="id_1111",
                    conversation_id="conv_111111111",
                    created_at=1735115982,
                    completed_at=None,
                    failed_at=None,
                    meta_data=None,
                    last_error=ChatError(code=0, msg=""),
                    status=ChatStatus.CREATED,
                    required_action=None,
                    usage=ChatUsage(token_count=0, output_count=0, input_count=0),
                ),
            ).model_dump()
        )
        assert events[len(events) - 1].event == ChatEventType.CONVERSATION_CHAT_COMPLETED

    def test_sync_chat_stream_error(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_workflows_chat_stream(respx_mock, read_file("testdata/chat_error_resp.txt"))
        stream = coze.workflows.chat.stream(workflow_id="workflow", bot_id="bot")
        assert stream
        assert stream.response.logid is not None
        assert stream.response.logid == mock_logid

        with pytest.raises(Exception, match="error event"):
            list(stream)

    def test_sync_chat_stream_json_error(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_workflows_chat_stream_json_fail(respx_mock)

        with pytest.raises(CozeAPIError, match="code: 4000, msg: json fail"):
            stream = coze.workflows.chat.stream(workflow_id="workflow", bot_id="bot")
            assert stream
            list(stream)

    def test_sync_chat_stream_failed(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_workflows_chat_stream(respx_mock, read_file("testdata/chat_failed_resp.txt"))
        stream = coze.workflows.chat.stream(workflow_id="workflow", bot_id="bot")
        assert stream
        assert stream.response.logid is not None
        assert stream.response.logid == mock_logid

        events = list(stream)
        assert events
        assert len(events) == 1
        assert events[0].chat.last_error.code == 5000

    def test_sync_chat_stream_invalid_event(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_workflows_chat_stream(respx_mock, read_file("testdata/chat_invalid_resp.txt"))

        stream = coze.workflows.chat.stream(workflow_id="workflow", bot_id="bot")
        assert stream
        assert stream.response.logid is not None
        assert stream.response.logid == mock_logid

        event = list(stream)[0]
        assert event.event == ChatEventType.UNKNOWN


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncWorkflowsChat:
    async def test_async_workflows_chat_stream(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_workflows_chat_stream(respx_mock, read_file("testdata/workflows_chat_stream_resp.txt"))
        stream = coze.workflows.chat.stream(workflow_id="workflow", bot_id="bot")
        events = [event async for event in stream]

        assert stream
        assert len(events) == 8
        assert (
            events[0].model_dump()
            == ChatEvent(
                event=ChatEventType.CONVERSATION_CHAT_CREATED,
                chat=Chat(
                    id="id_1111",
                    conversation_id="conv_111111111",
                    created_at=1735115982,
                    completed_at=None,
                    failed_at=None,
                    meta_data=None,
                    last_error=ChatError(code=0, msg=""),
                    status=ChatStatus.CREATED,
                    required_action=None,
                    usage=ChatUsage(token_count=0, output_count=0, input_count=0),
                ),
            ).model_dump()
        )
        assert events[len(events) - 1].event == ChatEventType.CONVERSATION_CHAT_COMPLETED

    async def test_async_chat_stream_error(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_workflows_chat_stream(respx_mock, read_file("testdata/chat_error_resp.txt"))
        stream = coze.workflows.chat.stream(workflow_id="workflow", bot_id="bot")
        assert stream

        with pytest.raises(Exception, match="error event"):
            _ = [event async for event in stream]

    async def test_async_chat_stream_json_error(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_workflows_chat_stream_json_fail(respx_mock)

        with pytest.raises(CozeAPIError, match="code: 4000, msg: json fail"):
            stream = coze.workflows.chat.stream(workflow_id="workflow", bot_id="bot")
            assert stream
            [event async for event in stream]

    async def test_async_chat_stream_failed(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_workflows_chat_stream(respx_mock, read_file("testdata/chat_failed_resp.txt"))
        stream = coze.workflows.chat.stream(workflow_id="workflow", bot_id="bot")
        assert stream

        events = [event async for event in stream]
        assert events
        assert len(events) == 1
        assert events[0].chat.last_error.code == 5000

    async def test_async_chat_stream_invalid_event(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_workflows_chat_stream(respx_mock, read_file("testdata/chat_invalid_resp.txt"))

        stream = coze.workflows.chat.stream(workflow_id="workflow", bot_id="bot")
        assert stream

        event = [event async for event in stream][0]
        assert event.event == ChatEventType.UNKNOWN
