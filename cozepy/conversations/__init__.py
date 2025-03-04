from typing import Any, Dict, List, Optional

from cozepy.chat import Message
from cozepy.model import AsyncNumberPaged, CozeModel, HTTPRequest, NumberPaged
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


class Conversation(CozeModel):
    id: str
    created_at: int
    meta_data: Dict[str, str]
    # section_id is used to distinguish the context sections of the session history. The same section is one context.
    last_section_id: str


class Section(CozeModel):
    id: str
    conversation_id: str


class _PrivateListConversationResp(CozeModel):
    has_more: bool
    conversations: List[Conversation]

    def get_total(self) -> Optional[int]:
        return None

    def get_has_more(self) -> Optional[bool]:
        return self.has_more

    def get_items(self) -> List[Conversation]:
        return self.conversations


class ConversationsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._messages = None

    def create(
        self,
        *,
        messages: Optional[List[Message]] = None,
        bot_id: Optional[str] = None,
        meta_data: Optional[Dict[str, str]] = None,
    ) -> Conversation:
        """
        Create a conversation.
        Conversation is an interaction between a bot and a user, including one or more messages.

        docs en: https://www.coze.com/docs/developer_guides/create_conversation
        docs zh: https://www.coze.cn/docs/developer_guides/create_conversation

        :param messages: Messages in the conversation. For more information, see EnterMessage object.
        :param bot_id: Bind and isolate conversation on different bots.
        :param meta_data: Additional information when creating a message, and this additional information will also be
        returned when retrieving messages.
        :return: Conversation object
        """
        url = f"{self._base_url}/v1/conversation/create"
        body: Dict[str, Any] = {
            "messages": [i.model_dump() for i in messages] if messages and len(messages) > 0 else [],
            "meta_data": meta_data,
        }
        if bot_id:
            body["bot_id"] = bot_id
        return self._requester.request("post", url, False, Conversation, body=body)

    def list(
        self,
        *,
        bot_id: str,
        page_num: int = 1,
        page_size: int = 50,
    ):
        url = f"{self._base_url}/v1/conversations"

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                params={
                    "bot_id": bot_id,
                    "page_num": i_page_num,
                    "page_size": i_page_size,
                },
                cast=_PrivateListConversationResp,
                stream=False,
            )

        return NumberPaged(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )

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

    def clear(self, *, conversation_id: str) -> Section:
        url = f"{self._base_url}/v1/conversations/{conversation_id}/clear"
        return self._requester.request("post", url, False, Section)

    @property
    def messages(self):
        if not self._messages:
            from .message import MessagesClient

            self._messages = MessagesClient(self._base_url, self._requester)
        return self._messages


class AsyncConversationsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._messages = None

    async def create(
        self,
        *,
        messages: Optional[List[Message]] = None,
        bot_id: Optional[str] = None,
        meta_data: Optional[Dict[str, str]] = None,
    ) -> Conversation:
        """
        Create a conversation.
        Conversation is an interaction between a bot and a user, including one or more messages.

        docs en: https://www.coze.com/docs/developer_guides/create_conversation
        docs zh: https://www.coze.cn/docs/developer_guides/create_conversation

        :param messages: Messages in the conversation. For more information, see EnterMessage object.
        :param bot_id: Bind and isolate conversation on different bots.
        :param meta_data: Additional information when creating a message, and this additional information will also be
        returned when retrieving messages.
        :return: Conversation object
        """
        url = f"{self._base_url}/v1/conversation/create"
        body: Dict[str, Any] = {
            "messages": [i.model_dump() for i in messages] if messages and len(messages) > 0 else [],
            "meta_data": meta_data,
        }
        if bot_id:
            body["bot_id"] = bot_id
        return await self._requester.arequest("post", url, False, Conversation, body=body)

    async def list(
        self,
        *,
        bot_id: str,
        page_num: int = 1,
        page_size: int = 50,
    ):
        url = f"{self._base_url}/v1/conversations"

        async def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "GET",
                url,
                params={
                    "bot_id": bot_id,
                    "page_num": i_page_num,
                    "page_size": i_page_size,
                },
                cast=_PrivateListConversationResp,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )

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

    async def clear(self, *, conversation_id: str) -> Section:
        url = f"{self._base_url}/v1/conversations/{conversation_id}/clear"
        return await self._requester.arequest("post", url, False, Section)

    @property
    def messages(self):
        if not self._messages:
            from .message import AsyncMessagesClient

            self._messages = AsyncMessagesClient(self._base_url, self._requester)
        return self._messages
