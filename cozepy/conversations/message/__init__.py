from typing import Dict, List

from cozepy.chat import MessageRole, MessageContentType, Message
from cozepy.auth import Auth
from cozepy.model import CozeModel, LastIDPaged
from cozepy.request import Requester


class MessageClient(object):
    """
    Message class.
    """

    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester

    def create(
        self,
        *,
        conversation_id: str,
        role: MessageRole,
        content: str,
        content_type: MessageContentType,
        meta_data: Dict[str, str] = None,
    ) -> Message:
        url = f"{self._base_url}/v1/conversation/message/create"
        params = {
            "conversation_id": conversation_id,
        }
        body = {
            "role": role,
            "content": content,
            "content_type": content_type,
            "meta_data": meta_data,
        }

        return self._requester.request("post", url, Message, params=params, body=body)

    def list(
        self,
        *,
        conversation_id: str,
        order: str = "desc",
        chat_id: str = None,
        before_id: str = None,
        after_id: str = None,
        limit: int = 50,
    ) -> LastIDPaged[Message]:
        url = f"{self._base_url}/v1/conversation/message/list"
        params = {
            "conversation_id": conversation_id,
        }
        body = {
            "order": order,
            "chat_id": chat_id,
            "before_id": before_id,
            "after_id": after_id,
            "limit": limit,
        }

        res = self._requester.request("post", url, self._PrivateListMessageResp, params=params, body=body)
        return LastIDPaged(res.items, res.first_id, res.last_id, res.has_more)

    def retrieve(
        self,
        *,
        conversation_id: str,
        message_id: str,
    ) -> Message:
        url = f"{self._base_url}/v1/conversation/message/retrieve"
        params = {
            "conversation_id": conversation_id,
            "message_id": message_id,
        }

        return self._requester.request("get", url, Message, params=params)

    def update(
        self,
        *,
        conversation_id: str,
        message_id: str,
        content: str = None,
        content_type: MessageContentType = None,
        meta_data: Dict[str, str] = None,
    ) -> Message:
        url = f"{self._base_url}/v1/conversation/message/modify"
        params = {
            "conversation_id": conversation_id,
            "message_id": message_id,
        }
        body = {
            "content": content,
            "content_type": content_type,
            "meta_data": meta_data,
        }

        return self._requester.request("post", url, Message, params=params, body=body, data_field="message")

    def delete(
        self,
        *,
        conversation_id: str,
        message_id: str,
        content: str = None,
        content_type: MessageContentType = None,
        meta_data: Dict[str, str] = None,
    ) -> Message:
        url = f"{self._base_url}/v1/conversation/message/delete"
        params = {
            "conversation_id": conversation_id,
            "message_id": message_id,
        }
        body = {
            "content": content,
            "content_type": content_type,
            "meta_data": meta_data,
        }

        return self._requester.request("post", url, Message, params=params, body=body)

    class _PrivateListMessageResp(CozeModel):
        first_id: str
        last_id: str
        has_more: bool
        items: List[Message]
