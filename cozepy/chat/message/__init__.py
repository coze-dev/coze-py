from typing import List

from cozepy.auth import Auth
from cozepy.chat import Message
from cozepy.request import Requester


class ChatMessagesClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester

    def list(
        self,
        *,
        conversation_id: str,
        chat_id: str,
    ) -> List[Message]:
        """
        The information of messages in the specified conversation besides the Query, including model replies,
        intermediate results of the Bot's execution, and other messages.

        docs en: https://www.coze.com/docs/developer_guides/list_chat_messages
        docs zh: https://www.coze.cn/docs/developer_guides/list_chat_messages

        :param conversation_id: The ID of the conversation.
        :param chat_id: The ID of the chat.
        :return: list of Message object
        """
        url = f"{self._base_url}/v3/chat/message/list"
        params = {
            "conversation_id": conversation_id,
            "chat_id": chat_id,
        }
        return self._requester.request("post", url, False, [Message], params=params)


class AsyncChatMessagesClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester

    async def list(
        self,
        *,
        conversation_id: str,
        chat_id: str,
    ) -> List[Message]:
        """
        The information of messages in the specified conversation besides the Query, including model replies,
        intermediate results of the Bot's execution, and other messages.

        docs en: https://www.coze.com/docs/developer_guides/list_chat_messages
        docs zh: https://www.coze.cn/docs/developer_guides/list_chat_messages

        :param conversation_id: The ID of the conversation.
        :param chat_id: The ID of the chat.
        :return: list of Message object
        """
        url = f"{self._base_url}/v3/chat/message/list"
        params = {
            "conversation_id": conversation_id,
            "chat_id": chat_id,
        }
        return await self._requester.arequest("post", url, False, [Message], params=params)
