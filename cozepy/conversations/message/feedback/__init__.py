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

    def delete(self, *, conversation_id: str, message_id: str, **kwargs) -> DeleteConversationMessageFeedbackResp:
        """
        删除消息评价

        删除指定消息的评价。 接口限制 仅会话创建者能删除对应会话中消息的评价。

        :param conversation_id: Conversation ID，即会话的唯一标识。可以在[发起对话](https://www.coze.cn/docs/developer_guides/chat_v3)接口 Response 中查看 conversation_id 字段。
        :param message_id: 待删除评价的消息 ID。你可以通过[查看对话消息详情](https://www.coze.cn/open/docs/developer_guides/list_chat_messages) API 返回的 Response 中查看消息 ID。 * 此消息必须在 conversation_id 指定的会话中。 * 仅支持评价以下来源的文本消息： * 通过发起对话 API 生成的 **type=answer** 类型的文本消息。 * 通过执行对话流 API 返回的文本消息。
        """
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

    async def delete(self, *, conversation_id: str, message_id: str, **kwargs) -> DeleteConversationMessageFeedbackResp:
        """
        删除消息评价

        删除指定消息的评价。 接口限制 仅会话创建者能删除对应会话中消息的评价。

        :param conversation_id: Conversation ID，即会话的唯一标识。可以在[发起对话](https://www.coze.cn/docs/developer_guides/chat_v3)接口 Response 中查看 conversation_id 字段。
        :param message_id: 待删除评价的消息 ID。你可以通过[查看对话消息详情](https://www.coze.cn/open/docs/developer_guides/list_chat_messages) API 返回的 Response 中查看消息 ID。 * 此消息必须在 conversation_id 指定的会话中。 * 仅支持评价以下来源的文本消息： * 通过发起对话 API 生成的 **type=answer** 类型的文本消息。 * 通过执行对话流 API 返回的文本消息。
        """
        url = f"{self._base_url}/v1/conversations/{conversation_id}/messages/{message_id}/feedback"
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest(
            "delete", url, False, cast=DeleteConversationMessageFeedbackResp, headers=headers
        )
