from typing import Any, Dict, List, Optional

from cozepy.chat import Message
from cozepy.model import AsyncNumberPaged, CozeModel, HTTPRequest, NumberPaged
from cozepy.request import Requester
from cozepy.util import dump_exclude_none, remove_url_trailing_slash


class Conversation(CozeModel):
    id: str
    created_at: int
    meta_data: Dict[str, str]
    # section_id is used to distinguish the context sections of the session history. The same section is one context.
    last_section_id: str
    name: Optional[str] = None
    updated_at: Optional[int] = None
    creator_id: Optional[str] = None
    connector_id: Optional[str] = None


class Section(CozeModel):
    id: str
    conversation_id: str


class DeleteConversationResp(CozeModel):
    """
    删除会话的响应结构体
    不包含任何字段，仅用于表示操作成功
    """


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
        name: Optional[str] = None,
        connector_id: Optional[str] = None,
        meta_data: Optional[Dict[str, str]] = None,
    ) -> Conversation:
        """
        创建会话。
        会话是Bot与用户之间的交互，包含一条或多条消息。

        docs en: https://www.coze.com/docs/developer_guides/create_conversation
        docs zh: https://www.coze.cn/docs/developer_guides/create_conversation

        :param messages: 会话中的消息列表。详细信息参见EnterMessage对象。
        :param bot_id: 绑定并隔离不同Bot的会话。
        :param name: 会话名称，最多100个字符。如果不传，则默认取首条消息内容作为名称。
        :param connector_id: 渠道ID，默认值为1024（API）。
        :param meta_data: 创建消息时的附加信息，这些信息在获取消息时也会返回。
        :return: Conversation对象
        """
        url = f"{self._base_url}/v1/conversation/create"
        body: Dict[str, Any] = dump_exclude_none(
            {
                "messages": messages,
                "meta_data": meta_data,
                "bot_id": bot_id,
                "name": name,
                "connector_id": connector_id,
            }
        )
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
        """
        清空会话内容。
        清空指定会话的所有消息内容，但保留会话本身。

        :param conversation_id: 会话ID
        :return: Section对象
        """
        url = f"{self._base_url}/v1/conversations/{conversation_id}/clear"
        return self._requester.request("post", url, False, Section)

    def update(self, *, conversation_id: str, name: Optional[str] = None) -> Conversation:
        """
        更新会话信息。
        更新指定会话的名称，便于识别与管理。

        docs: https://www.coze.cn/docs/developer_guides/edit_conversation

        :param conversation_id: 会话ID
        :param name: 新的会话名称，最多100个字符
        :return: 更新后的Conversation对象
        """
        url = f"{self._base_url}/v1/conversations/{conversation_id}"
        body = {"name": name}
        return self._requester.request("put", url, False, Conversation, body=body)

    def delete(self, *, conversation_id: str) -> DeleteConversationResp:
        """
        删除指定的会话。
        删除后会话及其中的所有消息都将被永久删除，无法恢复。

        docs: https://www.coze.cn/docs/developer_guides/delete_conversation

        :param conversation_id: 要删除的会话ID
        :return: DeleteConversationResp对象表示删除成功
        """
        url = f"{self._base_url}/v1/conversations/{conversation_id}"
        return self._requester.request("delete", url, False, DeleteConversationResp)

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
        name: Optional[str] = None,
        connector_id: Optional[str] = None,
        meta_data: Optional[Dict[str, str]] = None,
    ) -> Conversation:
        """
        创建会话。
        会话是Bot与用户之间的交互，包含一条或多条消息。

        docs en: https://www.coze.com/docs/developer_guides/create_conversation
        docs zh: https://www.coze.cn/docs/developer_guides/create_conversation

        :param messages: 会话中的消息列表。详细信息参见EnterMessage对象。
        :param bot_id: 绑定并隔离不同Bot的会话。
        :param name: 会话名称，最多100个字符。如果不传，则默认取首条消息内容作为名称。
        :param connector_id: 渠道ID，默认值为1024（API）。
        :param meta_data: 创建消息时的附加信息，这些信息在获取消息时也会返回。
        :return: Conversation对象
        """
        url = f"{self._base_url}/v1/conversation/create"
        body: Dict[str, Any] = dump_exclude_none(
            {
                "messages": messages,
                "meta_data": meta_data,
                "bot_id": bot_id,
                "name": name,
                "connector_id": connector_id,
            }
        )
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
        """
        清空会话内容。
        清空指定会话的所有消息内容，但保留会话本身。

        :param conversation_id: 会话ID
        :return: Section对象
        """
        url = f"{self._base_url}/v1/conversations/{conversation_id}/clear"
        return await self._requester.arequest("post", url, False, Section)

    async def update(self, *, conversation_id: str, name: Optional[str] = None) -> Conversation:
        """
        更新会话信息。
        更新指定会话的名称，便于识别与管理。

        docs: https://www.coze.cn/docs/developer_guides/edit_conversation

        :param conversation_id: 会话ID
        :param name: 新的会话名称，最多100个字符
        :return: 更新后的Conversation对象
        """
        url = f"{self._base_url}/v1/conversations/{conversation_id}"
        body = {"name": name}
        return await self._requester.arequest("put", url, False, Conversation, body=body)

    async def delete(self, *, conversation_id: str) -> DeleteConversationResp:
        """
        删除指定的会话。
        删除后会话及其中的所有消息都将被永久删除，无法恢复。

        docs: https://www.coze.cn/docs/developer_guides/delete_conversation

        :param conversation_id: 要删除的会话ID
        :return: DeleteConversationResp对象表示删除成功
        """
        url = f"{self._base_url}/v1/conversations/{conversation_id}"
        return await self._requester.arequest("delete", url, False, DeleteConversationResp)

    @property
    def messages(self):
        if not self._messages:
            from .message import AsyncMessagesClient

            self._messages = AsyncMessagesClient(self._base_url, self._requester)
        return self._messages
