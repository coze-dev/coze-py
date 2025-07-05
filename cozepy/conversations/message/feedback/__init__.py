from enum import Enum
from typing import List, Optional

from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash


class FeedbackType(str, Enum):
    """
    反馈类型
    """

    LIKE = "like"  # 赞
    UNLIKE = "unlike"  # 踩


class CreateConversationMessageFeedbackResp(CozeModel):
    pass


class DeleteConversationMessageFeedbackResp(CozeModel):
    pass


class ConversationsMessagesFeedbackClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(
        self,
        *,
        conversation_id: str,
        message_id: str,
        feedback_type: FeedbackType,
        reason_types: Optional[List[str]] = None,
        comment: Optional[str] = None,
        **kwargs,
    ) -> CreateConversationMessageFeedbackResp:
        url = f"{self._base_url}/v1/conversations/{conversation_id}/messages/{message_id}/feedback"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "feedback_type": feedback_type,
                "reason_types": reason_types,
                "comment": comment,
            }
        )

        return self._requester.request(
            "post", url, False, body=body, cast=CreateConversationMessageFeedbackResp, headers=headers
        )

    def delete(
        self,
        *,
        conversation_id: str,
        message_id: str,
        **kwargs,
    ) -> DeleteConversationMessageFeedbackResp:
        url = f"{self._base_url}/v1/conversations/{conversation_id}/messages/{message_id}/feedback"
        headers: Optional[dict] = kwargs.get("headers")

        return self._requester.request(
            "delete", url, False, cast=DeleteConversationMessageFeedbackResp, headers=headers
        )


class AsyncMessagesFeedbackClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def create(
        self,
        *,
        conversation_id: str,
        message_id: str,
        feedback_type: FeedbackType,
        reason_types: Optional[List[str]] = None,
        comment: Optional[str] = None,
        **kwargs,
    ) -> CreateConversationMessageFeedbackResp:
        url = f"{self._base_url}/v1/conversations/{conversation_id}/messages/{message_id}/feedback"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "feedback_type": feedback_type,
                "reason_types": reason_types,
                "comment": comment,
            }
        )

        return await self._requester.arequest(
            "post", url, False, body=body, cast=CreateConversationMessageFeedbackResp, headers=headers
        )

    async def delete(
        self,
        *,
        conversation_id: str,
        message_id: str,
        **kwargs,
    ) -> DeleteConversationMessageFeedbackResp:
        url = f"{self._base_url}/v1/conversations/{conversation_id}/messages/{message_id}/feedback"
        headers: Optional[dict] = kwargs.get("headers")

        return await self._requester.arequest(
            "delete", url, False, cast=DeleteConversationMessageFeedbackResp, headers=headers
        )
