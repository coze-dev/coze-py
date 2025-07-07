import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Coze, TokenAuth
from cozepy.conversations.message.feedback import (
    CreateConversationMessageFeedbackResp,
    DeleteConversationMessageFeedbackResp,
    FeedbackType,
)
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_create_conversation_message_feedback(respx_mock) -> CreateConversationMessageFeedbackResp:
    resp = CreateConversationMessageFeedbackResp()
    resp._raw_response = httpx.Response(
        200,
        json=resp.model_dump(),
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.post("/v1/conversations/conversation_id/messages/message_id/feedback").mock(resp._raw_response)
    return resp


def mock_delete_conversation_message_feedback(respx_mock) -> DeleteConversationMessageFeedbackResp:
    resp = DeleteConversationMessageFeedbackResp()
    resp._raw_response = httpx.Response(
        200,
        json=resp.model_dump(),
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.delete("/v1/conversations/conversation_id/messages/message_id/feedback").mock(resp._raw_response)
    return resp


@pytest.mark.respx(base_url="https://api.coze.com")
class TestConversationMessageFeedback:
    def test_sync_conversation_message_feedback_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_resp = mock_create_conversation_message_feedback(respx_mock)

        feedback = coze.conversations.messages.feedback.create(
            conversation_id="conversation_id",
            message_id="message_id",
            feedback_type=FeedbackType.LIKE,
            reason_types=["reason1", "reason2"],
            comment="test comment",
        )
        assert feedback
        assert feedback.response.logid == mock_resp.response.logid

    def test_sync_conversation_message_feedback_create_minimal(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_resp = mock_create_conversation_message_feedback(respx_mock)

        feedback = coze.conversations.messages.feedback.create(
            conversation_id="conversation_id",
            message_id="message_id",
            feedback_type=FeedbackType.UNLIKE,
        )
        assert feedback
        assert feedback.response.logid == mock_resp.response.logid

    def test_sync_conversation_message_feedback_delete(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_resp = mock_delete_conversation_message_feedback(respx_mock)

        feedback = coze.conversations.messages.feedback.delete(
            conversation_id="conversation_id",
            message_id="message_id",
        )
        assert feedback
        assert feedback.response.logid == mock_resp.response.logid

    def test_feedback_type_enum(self):
        """测试反馈类型枚举值"""
        assert FeedbackType.LIKE == "like"
        assert FeedbackType.UNLIKE == "unlike"


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncConversationMessageFeedback:
    async def test_async_conversation_message_feedback_create(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_resp = mock_create_conversation_message_feedback(respx_mock)

        feedback = await coze.conversations.messages.feedback.create(
            conversation_id="conversation_id",
            message_id="message_id",
            feedback_type=FeedbackType.LIKE,
            reason_types=["reason1", "reason2"],
            comment="test comment",
        )
        assert feedback
        assert feedback.response.logid == mock_resp.response.logid

    async def test_async_conversation_message_feedback_create_minimal(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_resp = mock_create_conversation_message_feedback(respx_mock)

        feedback = await coze.conversations.messages.feedback.create(
            conversation_id="conversation_id",
            message_id="message_id",
            feedback_type=FeedbackType.LIKE,
        )
        assert feedback
        assert feedback.response.logid == mock_resp.response.logid

    async def test_async_conversation_message_feedback_delete(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_resp = mock_delete_conversation_message_feedback(respx_mock)

        feedback = await coze.conversations.messages.feedback.delete(
            conversation_id="conversation_id",
            message_id="message_id",
        )
        assert feedback
        assert feedback.response.logid == mock_resp.response.logid
