from typing import Dict, List, Optional

from cozepy.auth import Auth
from cozepy.chat import Message
from cozepy.model import CozeModel
from cozepy.request import Requester


class Conversation(CozeModel):
    id: str
    created_at: int
    meta_data: Dict[str, str]


class ConversationsClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester
        self._messages = None

    def create(
        self, *, messages: Optional[List[Message]] = None, meta_data: Optional[Dict[str, str]] = None
    ) -> Conversation:
        """
        Create a conversation.
        Conversation is an interaction between a bot and a user, including one or more messages.

        docs en: https://www.coze.com/docs/developer_guides/create_conversation
        docs zh: https://www.coze.cn/docs/developer_guides/create_conversation

        :param messages: Messages in the conversation. For more information, see EnterMessage object.
        :param meta_data: Additional information when creating a message, and this additional information will also be
        returned when retrieving messages.
        :return: Conversation object
        """
        url = f"{self._base_url}/v1/conversation/create"
        body = {
            "messages": [i.model_dump() for i in messages] if messages and len(messages) > 0 else [],
            "meta_data": meta_data,
        }
        return self._requester.request("post", url, False, Conversation, body=body)

    def retrieve(self, *, conversation_id: str) -> Conversation:
        """
        Get the information of specific conversation.

        docs en: https://www.coze.com/docs/developer_guides/retrieve_conversation
        docs cn: https://www.coze.cn/docs/developer_guides/retrieve_conversation

        :param conversation_id: The ID of the conversation.
        :return: Conversation object
        """
        url = f"{self._base_url}/v1/conversation/retrieve"
        params = {
            "conversation_id": conversation_id,
        }
        return self._requester.request("get", url, False, Conversation, params=params)

    @property
    def messages(self):
        if not self._messages:
            from .message import MessagesClient

            self._messages = MessagesClient(self._base_url, self._auth, self._requester)
        return self._messages


class AsyncConversationsClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester
        self._messages = None

    async def create(
        self, *, messages: Optional[List[Message]] = None, meta_data: Optional[Dict[str, str]] = None
    ) -> Conversation:
        """
        Create a conversation.
        Conversation is an interaction between a bot and a user, including one or more messages.

        docs en: https://www.coze.com/docs/developer_guides/create_conversation
        docs zh: https://www.coze.cn/docs/developer_guides/create_conversation

        :param messages: Messages in the conversation. For more information, see EnterMessage object.
        :param meta_data: Additional information when creating a message, and this additional information will also be
        returned when retrieving messages.
        :return: Conversation object
        """
        url = f"{self._base_url}/v1/conversation/create"
        body = {
            "messages": [i.model_dump() for i in messages] if messages and len(messages) > 0 else [],
            "meta_data": meta_data,
        }
        return await self._requester.arequest("post", url, False, Conversation, body=body)

    async def retrieve(self, *, conversation_id: str) -> Conversation:
        """
        Get the information of specific conversation.

        docs en: https://www.coze.com/docs/developer_guides/retrieve_conversation
        docs cn: https://www.coze.cn/docs/developer_guides/retrieve_conversation

        :param conversation_id: The ID of the conversation.
        :return: Conversation object
        """
        url = f"{self._base_url}/v1/conversation/retrieve"
        params = {
            "conversation_id": conversation_id,
        }
        return await self._requester.arequest("get", url, False, Conversation, params=params)

    @property
    def messages(self):
        if not self._messages:
            from .message import AsyncMessagesClient

            self._messages = AsyncMessagesClient(self._base_url, self._auth, self._requester)
        return self._messages
