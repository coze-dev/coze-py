import base64
import os
import tempfile

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
    Message,
    MessageObjectString,
    TokenAuth,
)
from cozepy.util import random_hex, write_pcm_to_wav_file
from tests.test_util import logid_key, read_file

import time
from unittest.mock import patch, AsyncMock


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


def mock_chat_create(respx_mock, conversation_id: str, status: ChatStatus):
    logid = random_hex(10)
    chat = make_chat(conversation_id, status)
    chat._raw_response = httpx.Response(200, json={"data": chat.model_dump()}, headers={logid_key(): logid})
    respx_mock.post("/v3/chat").mock(chat._raw_response)
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
    chat = make_chat(conversation_id, status)
    chat._raw_response = httpx.Response(
        200,
        json={"data": chat.model_dump()},
        headers={logid_key(): logid},
    )
    respx_mock.post("/v3/chat/retrieve").mock(chat._raw_response)
    return logid


def mock_chat_submit_tool_outputs(respx_mock, conversation_id: str, status: ChatStatus):
    logid = random_hex(10)
    chat = make_chat(conversation_id, status)
    chat._raw_response = httpx.Response(
        200,
        json={"data": chat.model_dump()},
        headers={logid_key(): logid},
    )
    respx_mock.post("/v3/chat/submit_tool_outputs").mock(chat._raw_response)
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
    chat = make_chat(conversation_id, status)
    chat._raw_response = httpx.Response(
        200,
        json={"data": chat.model_dump()},
        headers={logid_key(): logid},
    )
    respx_mock.post("/v3/chat/cancel").mock(chat._raw_response)
    return logid


def mock_chat_poll(
    respx_mock,
    conversation_id: str,
):
    chat_in_progress = make_chat(conversation_id, ChatStatus.IN_PROGRESS)
    chat_in_progress._raw_response = httpx.Response(
        200,
        json={"data": chat_in_progress.model_dump()},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.post("/v3/chat").mock(chat_in_progress._raw_response)

    chat_completed = make_chat(conversation_id, ChatStatus.COMPLETED)
    chat_completed._raw_response = httpx.Response(
        200,
        json={"data": chat_completed.model_dump()},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.post("/v3/chat/retrieve").mock(chat_completed._raw_response)

    msg = Message.build_user_question_text("hi")
    list_message_logid = random_hex(10)
    respx_mock.get("/v3/chat/message/list").mock(
        httpx.Response(
            200,
            json={"data": [msg.model_dump()]},
            headers={logid_key(): list_message_logid},
        )
    )
    return chat_completed, list_message_logid


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
        assert res.response.logid is not None
        assert res.response.logid == mock_logid
        assert res.conversation_id == conversation_id

    def test_sync_chat_stream(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_chat_stream(respx_mock, read_file("testdata/chat_text_stream_resp.txt"))
        stream = coze.chat.stream(bot_id="bot", user_id="user")

        assert stream
        assert stream.response.logid == mock_logid

        events = list(stream)
        assert len(events) == 8
        assert (
            events[0].model_dump()
            == ChatEvent(
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
            ).model_dump()
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
        assert stream.response.logid is not None
        assert stream.response.logid == mock_logid

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
        assert stream.response.logid is not None
        assert stream.response.logid == mock_logid

        with pytest.raises(Exception, match="error event"):
            list(stream)

    def test_sync_chat_stream_failed(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_chat_stream(respx_mock, read_file("testdata/chat_failed_resp.txt"))
        stream = coze.chat.stream(bot_id="bot", user_id="user")
        assert stream
        assert stream.response.logid is not None
        assert stream.response.logid == mock_logid

        events = list(stream)
        assert events
        assert len(events) == 1
        assert events[0].chat.last_error.code == 5000

    def test_sync_chat_stream_invalid_event(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_chat_stream(respx_mock, read_file("testdata/chat_invalid_resp.txt"))

        stream = coze.chat.stream(bot_id="bot", user_id="user")
        assert stream
        assert stream.response.logid is not None
        assert stream.response.logid == mock_logid

        with pytest.raises(Exception, match="invalid chat.event: invalid"):
            list(stream)

    def test_sync_chat_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        mock_logid = mock_chat_retrieve(respx_mock, conversation_id, ChatStatus.FAILED)
        res = coze.chat.retrieve(conversation_id=conversation_id, chat_id="chat")

        assert res
        assert res.response.logid is not None
        assert res.response.logid == mock_logid
        assert res.conversation_id == conversation_id

    def test_sync_submit_tool_outputs_not_stream(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        mock_logid = mock_chat_submit_tool_outputs(respx_mock, conversation_id, ChatStatus.FAILED)
        res = coze.chat.submit_tool_outputs(
            conversation_id=conversation_id, chat_id="chat", tool_outputs=[], stream=False
        )

        assert res
        assert res.response.logid is not None
        assert res.response.logid == mock_logid
        assert res.conversation_id == conversation_id

    def test_sync_submit_tool_outputs_stream(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_chat_submit_tool_outputs_stream(respx_mock, read_file("testdata/chat_text_stream_resp.txt"))
        stream = coze.chat.submit_tool_outputs(
            conversation_id="conversation", chat_id="chat", tool_outputs=[], stream=True
        )
        assert stream
        assert stream.response.logid is not None
        assert stream.response.logid == mock_logid

        events = list(stream)
        assert events
        assert len(events) == 8
        assert (
            events[0].model_dump()
            == ChatEvent(
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
            ).model_dump()
        )
        assert events[len(events) - 1].event == ChatEventType.CONVERSATION_CHAT_COMPLETED

    def test_sync_chat_cancel(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        mock_logid = mock_chat_cancel(respx_mock, conversation_id, ChatStatus.FAILED)
        res = coze.chat.cancel(conversation_id="conversation", chat_id="chat")

        assert res
        assert res.response.logid is not None
        assert res.response.logid == mock_logid
        assert res.conversation_id == conversation_id

    def test_sync_chat_cancel_direct_call(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        conversation_id = "conv_id_cancel_direct"
        chat_id = "chat_id_cancel_direct"

        # Mock the cancel API endpoint call
        # The `cancel` method now directly calls the cancel endpoint.
        # `mock_chat_cancel` sets up respx_mock for POST /v3/chat/cancel
        # and returns a Chat object (e.g., with status CANCELED or FAILED as per its setup)
        expected_status = ChatStatus.CANCELED  # Or ChatStatus.FAILED, depending on mock_chat_cancel
        mock_cancel_logid = mock_chat_cancel(respx_mock, conversation_id, expected_status)

        res = coze.chat.cancel(conversation_id=conversation_id, chat_id=chat_id)

        assert res is not None
        assert res.response.logid == mock_cancel_logid  # Ensure the cancel endpoint was hit
        assert res.status == expected_status
        assert res.conversation_id == conversation_id  # As per make_chat in mock_chat_cancel

        # Ensure only one call was made (to the cancel endpoint)
        assert len(respx_mock.calls) == 1
        cancel_call = respx_mock.calls.last
        assert "cancel" in str(cancel_call.request.url)
        assert (
            cancel_call.request.content
            == b'{"conversation_id": "conv_id_cancel_direct", "chat_id": "chat_id_cancel_direct"}'
        )

    def test_sync_chat_poll(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        conversation_id = "conversation_id"
        mock_chat, mock_logid = mock_chat_poll(
            respx_mock,
            conversation_id,
        )

        res = coze.chat.create_and_poll(bot_id="bot", user_id="user")

        assert res
        assert res.chat.response.logid == mock_chat.response.logid
        assert res.chat.conversation_id == conversation_id
        assert res.messages
        assert res.messages[0].content == "hi"

    @patch("time.time")
    @patch("time.sleep", return_value=None)  # Mock sleep to do nothing and speed up test
    def test_sync_chat_create_and_poll_timeout_branches(self, mock_sleep, mock_time, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        bot_id = "test_bot"
        user_id = "test_user"
        conversation_id = "poll_conv_id"
        chat_id = "id"  # from make_chat
        poll_timeout_seconds = 5

        # --- Scenario 1: Chat becomes COMPLETED right before cancel would be called ---
        respx_mock.reset()  # Clear routes from other tests
        initial_chat_create_logid = mock_chat_create(respx_mock, conversation_id, ChatStatus.IN_PROGRESS)

        # Mocks for time to control the polling loop.
        # Scenario A: Loop terminates due to status change (COMPLETED).
        mock_time.side_effect = [
            0,  # Initial start time for create_and_poll
            1,  # time.time() for first poll loop timeout check
            2,  # time.time() for second poll loop timeout check
        ]

        # Define sequenced responses for retrieve in Scenario A
        scenario_a_retrieve_responses = [
            httpx.Response(200, json={"data": make_chat(conversation_id, ChatStatus.IN_PROGRESS).model_dump()}),
            httpx.Response(200, json={"data": make_chat(conversation_id, ChatStatus.COMPLETED).model_dump()}),
        ]

        def retrieve_side_effect_scen_a(request):
            if not scenario_a_retrieve_responses:
                raise AssertionError("retrieve_side_effect_scen_a called too many times")
            return scenario_a_retrieve_responses.pop(0)

        respx_mock.post("/v3/chat/retrieve").mock(side_effect=retrieve_side_effect_scen_a)

        # Mock messages.list (should be called for Scenario A)
        mock_list_messages_logid = random_hex(10)
        respx_mock.get("/v3/chat/message/list").mock(
            return_value=httpx.Response(
                200,
                json={"data": [Message.build_user_question_text("msg").model_dump()]},
                headers={logid_key(): mock_list_messages_logid},
            )
        )

        # Ensure cancel is NOT called
        cancel_route = respx_mock.post("/v3/chat/cancel")

        poll_result_completed = coze.chat.create_and_poll(
            bot_id=bot_id, user_id=user_id, conversation_id=conversation_id, poll_timeout=poll_timeout_seconds
        )

        assert poll_result_completed.chat.status == ChatStatus.COMPLETED
        assert not cancel_route.called  # Cancel should not have been called
        assert respx_mock.get("/v3/chat/message/list").called  # Messages list should be called
        # Expect 2 retrieve calls: one for each poll loop.
        assert respx_mock.calls_by_namespace("post /v3/chat/retrieve").call_count == 2
        assert len(scenario_a_retrieve_responses) == 0  # Ensure all mocked responses were consumed

        # --- Scenario 2: Chat is still IN_PROGRESS at timeout, so cancel IS called ---
        respx_mock.reset()  # Clear routes for Scenario B
        mock_chat_create(respx_mock, conversation_id, ChatStatus.IN_PROGRESS)  # Initial create

        # Scenario B: Poll once (IN_PROGRESS), then timeout condition is met, leading to cancel.
        mock_time.side_effect = [
            0,  # Initial start time for create_and_poll
            1,  # time.time() for first poll's timeout check (1-0 < 5 is true)
            # This next time.time() call is for the main timeout check, causing cancel path
            poll_timeout_seconds + 1,  # Timeout condition met (e.g., 6-0 > 5)
        ]

        # Mock retrieve call for Scenario B: always IN_PROGRESS
        # This single mock will handle the one retrieve call in the loop.
        respx_mock.post("/v3/chat/retrieve").mock(
            return_value=httpx.Response(
                200, json={"data": make_chat(conversation_id, ChatStatus.IN_PROGRESS).model_dump()}
            )
        )

        # Mock cancel (should be called for Scenario B)
        cancel_logid = mock_chat_cancel(respx_mock, conversation_id, ChatStatus.CANCELED)  # Sets up its own route

        # Ensure messages.list is NOT called for this path
        list_messages_route = respx_mock.get("/v3/chat/message/list")

        poll_result_canceled = coze.chat.create_and_poll(
            bot_id=bot_id, user_id=user_id, conversation_id=conversation_id, poll_timeout=poll_timeout_seconds
        )

        assert poll_result_canceled.chat.status == ChatStatus.CANCELED
        assert poll_result_canceled.chat.response.logid == cancel_logid  # Logid from the cancel call
        assert respx_mock.post("/v3/chat/cancel").called  # Ensure cancel endpoint was hit
        assert not list_messages_route.called  # Messages list should NOT be called
        # Expect 1 retrieve call: one poll loop before timeout check.
        assert respx_mock.calls_by_namespace("post /v3/chat/retrieve").call_count == 1




@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncChatConversationMessage:  # Consider renaming to TestAsyncChat for consistency
    async def test_async_chat_create(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        conversation_id = "conversation_id"
        mock_logid = mock_chat_create(respx_mock, conversation_id, ChatStatus.FAILED)
        res = await coze.chat.create(bot_id="bot", user_id="user")

        assert res
        assert res.response.logid is not None
        assert res.response.logid == mock_logid
        assert res.conversation_id == conversation_id

    async def test_async_chat_cancel_direct_call(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        conversation_id = "conv_id_async_cancel_direct"
        chat_id = "chat_id_async_cancel_direct"

        expected_status = ChatStatus.CANCELED
        mock_cancel_logid = mock_chat_cancel(respx_mock, conversation_id, expected_status)

        res = await coze.chat.cancel(conversation_id=conversation_id, chat_id=chat_id)

        assert res is not None
        assert res.response.logid == mock_cancel_logid
        assert res.status == expected_status
        assert res.conversation_id == conversation_id

        assert len(respx_mock.calls) == 1
        cancel_call = respx_mock.calls.last
        assert "cancel" in str(cancel_call.request.url)
        assert (
            cancel_call.request.content
            == b'{"conversation_id": "conv_id_async_cancel_direct", "chat_id": "chat_id_async_cancel_direct"}'
        )

    async def test_async_chat_stream(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_chat_stream(respx_mock, read_file("testdata/chat_text_stream_resp.txt"))
        stream = coze.chat.stream(bot_id="bot", user_id="user")
        events = [event async for event in stream]

        assert stream
        assert len(events) == 8
        assert (
            events[0].model_dump()
            == ChatEvent(
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
            ).model_dump()
        )
        assert events[len(events) - 1].event == ChatEventType.CONVERSATION_CHAT_COMPLETED

    async def test_async_chat_audio_stream(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

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
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_logid = mock_chat_stream(respx_mock, read_file("testdata/chat_error_resp.txt"))  # noqa: F841
        stream = coze.chat.stream(bot_id="bot", user_id="user")
        assert stream
        with pytest.raises(Exception, match="error event"):
            [event async for event in stream]

    async def test_async_chat_stream_failed(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_logid = mock_chat_stream(respx_mock, read_file("testdata/chat_failed_resp.txt"))  # noqa: F841
        stream = coze.chat.stream(bot_id="bot", user_id="user")
        assert stream
        events = [event async for event in stream]
        assert events
        assert len(events) == 1
        assert events[0].chat.last_error.code == 5000

    async def test_async_chat_stream_invalid_event(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_logid = mock_chat_stream(respx_mock, read_file("testdata/chat_invalid_resp.txt"))  # noqa: F841

        stream = coze.chat.stream(bot_id="bot", user_id="user")
        assert stream
        with pytest.raises(Exception, match="invalid chat.event: invalid"):
            [event async for event in stream]

    async def test_async_chat_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        conversation_id = "conversation_id"
        mock_logid = mock_chat_retrieve(respx_mock, conversation_id, ChatStatus.FAILED)
        res = await coze.chat.retrieve(conversation_id=conversation_id, chat_id="chat")

        assert res
        assert res.response.logid is not None
        assert res.response.logid == mock_logid
        assert res.conversation_id == conversation_id

    async def test_async_submit_tool_outputs_not_stream(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        conversation_id = "conversation_id"
        mock_logid = mock_chat_submit_tool_outputs(respx_mock, conversation_id, ChatStatus.FAILED)
        res = await coze.chat.submit_tool_outputs(conversation_id=conversation_id, chat_id="chat", tool_outputs=[])

        assert res
        assert res.response.logid is not None
        assert res.response.logid == mock_logid
        assert res.conversation_id == conversation_id

    async def test_async_submit_tool_outputs_stream(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_chat_submit_tool_outputs_stream(respx_mock, read_file("testdata/chat_text_stream_resp.txt"))
        stream = coze.chat.submit_tool_outputs_stream(conversation_id="conversation", chat_id="chat", tool_outputs=[])
        assert stream
        events = [event async for event in stream]
        assert events
        assert len(events) == 8
        assert (
            events[0].model_dump()
            == ChatEvent(
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
            ).model_dump()
        )
        assert events[len(events) - 1].event == ChatEventType.CONVERSATION_CHAT_COMPLETED

    async def test_async_chat_cancel(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        conversation_id = "conversation_id"
        mock_logid = mock_chat_cancel(respx_mock, conversation_id, ChatStatus.FAILED)
        res = await coze.chat.cancel(conversation_id="conversation", chat_id="chat")

        assert res
        assert res.response.logid is not None
        assert res.response.logid == mock_logid
        assert res.conversation_id == conversation_id
