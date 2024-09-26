from typing import List

from cozepy.auth import Auth
from cozepy.chat.v3 import Message
from cozepy.request import Requester


class MessageClient(object):
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
        Create a conversation.
        Conversation is an interaction between a bot and a user, including one or more messages.
        """
        url = f"{self._base_url}/v3/chat/message/list"
        params = {
            "conversation_id": conversation_id,
            "chat_id": chat_id,
        }
        return self._requester.request("post", url, List[Message], params=params)
