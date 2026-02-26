from typing import TYPE_CHECKING, Dict, List, Optional

from cozepy.chat import Message, MessageContentType, MessageRole
from cozepy.model import AsyncLastIDPaged, CozeModel, HTTPRequest, LastIDPaged, LastIDPagedResponse
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash

if TYPE_CHECKING:
    from .feedback import AsyncMessagesFeedbackClient, ConversationsMessagesFeedbackClient


class _PrivateListMessageResp(CozeModel, LastIDPagedResponse[Message]):
    first_id: str
    last_id: str
    has_more: bool
    items: List[Message]

    def get_first_id(self) -> str:
        return self.first_id

    def get_last_id(self) -> str:
        return self.last_id

    def get_has_more(self) -> bool:
        return self.has_more

    def get_items(self) -> List[Message]:
        return self.items


class MessagesClient(object):
    """
    Message class.
    """

    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

        self._feedback: Optional["ConversationsMessagesFeedbackClient"] = None

    def create(
        self,
        *,
        conversation_id: str,
        role: MessageRole,
        content: str,
        content_type: MessageContentType,
        meta_data: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Message:
        """
        创建消息

        创建一条消息，并将其添加到指定的会话中。
        会话、对话和消息的概念说明，可参考[基础概念](https://www.coze.cn/docs/developer_guides/coze_api_overview#4a288f73)。
        消息在服务端的保存时长为 180 天，到期后自动删除。你也可以调用[删除消息](https://www.coze.cn/docs/developer_guides/delete_message)接口，手动从会话中删除消息。
        你可以通过[查看消息列表](https://www.coze.cn/open/docs/developer_guides/list_message)查询指定会话（conversation）中的所有消息。

        :param conversation_id: Conversation ID，即会话的唯一标识。你可以在[发起对话](https://www.coze.cn/docs/developer_guides/chat_v3)接口 Response 中查看 conversation_id 字段。
        :param role: 已TODO 字段打平
        :param content: 内容
        """
        url = f"{self._base_url}/v1/conversation/message/create"
        params = {
            "conversation_id": conversation_id,
        }
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "role": role,
            "content": content,
            "content_type": content_type,
            "meta_data": meta_data,
        }
        return self._requester.request("post", url, False, cast=Message, params=params, headers=headers, body=body)

    def retrieve(
        self,
        *,
        conversation_id: str,
        message_id: str,
        **kwargs,
    ) -> Message:
        """
        查看消息详情

        查看指定消息的详细信息。

        :param conversation_id: Conversation ID，即会话的唯一标识。你可以在[发起对话](https://www.coze.cn/docs/developer_guides/chat_v3)接口 Response 中查看 conversation_id 字段的值。
        :param message_id: Message ID，即消息的唯一标识。
        """
        url = f"{self._base_url}/v1/conversation/message/retrieve"
        params = {
            "conversation_id": conversation_id,
            "message_id": message_id,
        }
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("get", url, False, cast=Message, params=params, headers=headers)

    def update(
        self,
        *,
        conversation_id: str,
        message_id: str,
        content: Optional[str] = None,
        content_type: Optional[MessageContentType] = None,
        meta_data: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Message:
        """
        修改消息

        修改一条消息，支持修改消息内容、附加内容和消息类型。

        :param conversation_id: Conversation ID，即会话的唯一标识。可以在[发起对话](https://www.coze.cn/docs/developer_guides/chat_v3)接口 Response 中查看 conversation_id 字段。
        :param message_id: Message ID，即消息的唯一标识。
        :param content: 内容
        """
        url = f"{self._base_url}/v1/conversation/message/modify"
        params = {
            "conversation_id": conversation_id,
            "message_id": message_id,
        }
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "content": content,
            "content_type": content_type,
            "meta_data": meta_data,
        }
        return self._requester.request(
            "post", url, False, cast=Message, params=params, headers=headers, body=body, data_field="message"
        )

    def delete(
        self,
        *,
        conversation_id: str,
        message_id: str,
        **kwargs,
    ) -> Message:
        """
        删除消息

        调用接口在指定会话中删除消息。
        暂不支持批量操作，需要逐条删除。
        删除指定 message id 对应的消息。如果消息 type=answer，会同步删除与之相关的 verbose、function_call 等中间态消息，但不支持仅删除某一条中间态消息。
        删除消息后，无法通过查看消息列表或查看对话消息详情接口查看已删除的这些消息。

        :param conversation_id: 待删除的消息所属的会话 ID。
        :param message_id: 待删除的消息 ID，你可以选择删除会话中的 question 消息和 answer 消息。 * 待删除消息必须属于 conversation_id 指定的会话。 * 仅支持删除 type=answer 或 question 的消息，不支持单独删除 function_call 等中间态消息。当删除 type=answer 的消息时，系统会同步删除与之关联的 function_call 等中间态消息。
        """
        url = f"{self._base_url}/v1/conversation/message/delete"
        params = {
            "conversation_id": conversation_id,
            "message_id": message_id,
        }
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("post", url, False, cast=Message, params=params, headers=headers)

    def list(
        self,
        *,
        conversation_id: str,
        order: str = "desc",
        chat_id: Optional[str] = None,
        before_id: Optional[str] = None,
        after_id: Optional[str] = None,
        limit: int = 50,
    ) -> LastIDPaged[Message]:
        """
        Get the message list of a specified conversation.

        docs en: https://www.coze.com/docs/developer_guides/list_message
        docs zh: https://www.coze.cn/docs/developer_guides/list_message

        :param conversation_id: The ID of the conversation.
        :param order: The sorting method for the message list.
        :param chat_id: The ID of the Chat.
        :param before_id: Get messages before the specified position.
        :param after_id: Get messages after the specified position.
        :param limit: The amount of data returned per query. Default is 50, with a range of 1 to 50.
        :return: The message list of the specified conversation.
        """
        url = f"{self._base_url}/v1/conversation/message/list"
        params = {
            "conversation_id": conversation_id,
        }

        def request_maker(i_before_id: str, i_after_id: str) -> HTTPRequest:
            return self._requester.make_request(
                "POST",
                url,
                json={
                    "order": order,
                    "chat_id": chat_id,
                    "before_id": i_before_id if i_before_id else None,
                    "after_id": i_after_id if i_after_id else None,
                    "limit": limit,
                },
                params=params,
                cast=_PrivateListMessageResp,
                stream=False,
            )

        return LastIDPaged(
            before_id=before_id or "",
            after_id=after_id or "",
            requestor=self._requester,
            request_maker=request_maker,
        )

    def _list_page(
        self,
        *,
        conversation_id: str,
        order: Optional[str] = "desc",
        chat_id: Optional[str] = None,
        before_id: Optional[str] = None,
        after_id: Optional[str] = None,
        limit: Optional[int] = 50,
        **kwargs,
    ) -> _PrivateListMessageResp:
        """
        查看消息列表

        查看指定会话的消息列表。
        **查看消息列表** API 与**查看对话消息详情** API 的区别在于：
        * **查看消息列表** API 用于查询指定会话（conversation）中的消息记录，不仅包括开发者在会话中手动插入的每一条消息和用户发送的 Query，也包括调用**发起对话** API 得到的 type=answer 的智能体回复，但不包括 type=function_call、tool_response 和 follow-up 类型的对话中间态消息。
        * **查看对话消息详情** API 通常用于非流式对话场景中，查看某次对话（chat）中 type=answer 的智能体回复及 type=function_call、tool_response 和 follow-up 类型类型的对话中间态消息。不包括用户发送的 Query。
        消息在服务端的保存时长为180天，期满后，消息将自动从会话的消息记录中删除。

        :param conversation_id: Conversation ID，即会话的唯一标识。可以在[发起对话](https://www.coze.cn/docs/developer_guides/chat_v3)接口 Response 中查看 conversation_id 字段。
        :param order: 查询顺序  desc倒序 asc正序 TODO 默认倒序
        :param chat_id: 运行id
        :param before_id: 前序消息游标ID  已TODO str
        :param after_id: 后序消息游标ID  已TODO str
        :param limit: 每页限制条数  TODO 限制50条
        """
        url = f"{self._base_url}/v1/conversation/message/list"
        params = {
            "conversation_id": conversation_id,
        }
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "order": order,
            "chat_id": chat_id,
            "before_id": before_id if before_id else None,
            "after_id": after_id if after_id else None,
            "limit": limit,
        }
        return self._requester.request(
            "post", url, False, cast=_PrivateListMessageResp, params=params, headers=headers, body=body
        )

    @property
    def feedback(self) -> "ConversationsMessagesFeedbackClient":
        if not self._feedback:
            from .feedback import ConversationsMessagesFeedbackClient

            self._feedback = ConversationsMessagesFeedbackClient(self._base_url, self._requester)
        return self._feedback


class AsyncMessagesClient(object):
    """
    Message class.
    """

    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

        self._feedback: Optional["AsyncMessagesFeedbackClient"] = None

    async def create(
        self,
        *,
        conversation_id: str,
        role: MessageRole,
        content: str,
        content_type: MessageContentType,
        meta_data: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Message:
        """
        创建消息

        创建一条消息，并将其添加到指定的会话中。
        会话、对话和消息的概念说明，可参考[基础概念](https://www.coze.cn/docs/developer_guides/coze_api_overview#4a288f73)。
        消息在服务端的保存时长为 180 天，到期后自动删除。你也可以调用[删除消息](https://www.coze.cn/docs/developer_guides/delete_message)接口，手动从会话中删除消息。
        你可以通过[查看消息列表](https://www.coze.cn/open/docs/developer_guides/list_message)查询指定会话（conversation）中的所有消息。

        :param conversation_id: Conversation ID，即会话的唯一标识。你可以在[发起对话](https://www.coze.cn/docs/developer_guides/chat_v3)接口 Response 中查看 conversation_id 字段。
        :param role: 已TODO 字段打平
        :param content: 内容
        """
        url = f"{self._base_url}/v1/conversation/message/create"
        params = {
            "conversation_id": conversation_id,
        }
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "role": role,
            "content": content,
            "content_type": content_type,
            "meta_data": meta_data,
        }
        return await self._requester.arequest(
            "post", url, False, cast=Message, params=params, headers=headers, body=body
        )

    async def retrieve(
        self,
        *,
        conversation_id: str,
        message_id: str,
        **kwargs,
    ) -> Message:
        """
        查看消息详情

        查看指定消息的详细信息。

        :param conversation_id: Conversation ID，即会话的唯一标识。你可以在[发起对话](https://www.coze.cn/docs/developer_guides/chat_v3)接口 Response 中查看 conversation_id 字段的值。
        :param message_id: Message ID，即消息的唯一标识。
        """
        url = f"{self._base_url}/v1/conversation/message/retrieve"
        params = {
            "conversation_id": conversation_id,
            "message_id": message_id,
        }
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest("get", url, False, cast=Message, params=params, headers=headers)

    async def update(
        self,
        *,
        conversation_id: str,
        message_id: str,
        content: Optional[str] = None,
        content_type: Optional[MessageContentType] = None,
        meta_data: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Message:
        """
        修改消息

        修改一条消息，支持修改消息内容、附加内容和消息类型。

        :param conversation_id: Conversation ID，即会话的唯一标识。可以在[发起对话](https://www.coze.cn/docs/developer_guides/chat_v3)接口 Response 中查看 conversation_id 字段。
        :param message_id: Message ID，即消息的唯一标识。
        :param content: 内容
        """
        url = f"{self._base_url}/v1/conversation/message/modify"
        params = {
            "conversation_id": conversation_id,
            "message_id": message_id,
        }
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "content": content,
            "content_type": content_type,
            "meta_data": meta_data,
        }
        return await self._requester.arequest(
            "post", url, False, cast=Message, params=params, headers=headers, body=body, data_field="message"
        )

    async def delete(
        self,
        *,
        conversation_id: str,
        message_id: str,
        **kwargs,
    ) -> Message:
        """
        删除消息
        暂不支持批量操作，需要逐条删除。
        删除指定 message id 对应的消息。
        如果消息 type=answer，会同步删除与之相关的 verbose、function_call 等中间态消息，但不支持仅删除某一条中间态消息。
        删除消息后，无法通过 查看消息列表 或 查看对话消息详情 接口查看已删除的这些消息。
        调用接口在指定会话中删除消息。
        :param conversation_id: 待删除的消息所属的会话 ID。
        :param message_id: 待删除的消息 ID，你可以选择删除会话中的 question 消息和 answer 消息。
        * 待删除消息必须属于 conversation_id 指定的会话。
        * 仅支持删除 type=answer 或 question 的消息，不支持单独删除 function_call 等中间态消息。
        当删除 type=answer 的消息时，系统会同步删除与之关联的 function_call 等中间态消息。
        """
        url = f"{self._base_url}/v1/conversation/message/delete"
        params = {
            "conversation_id": conversation_id,
            "message_id": message_id,
        }
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest("post", url, False, cast=Message, params=params, headers=headers)

    async def list(
        self,
        *,
        conversation_id: str,
        order: str = "desc",
        chat_id: Optional[str] = None,
        before_id: Optional[str] = None,
        after_id: Optional[str] = None,
        limit: int = 50,
    ) -> AsyncLastIDPaged[Message]:
        """
        Get the message list of a specified conversation.

        docs en: https://www.coze.com/docs/developer_guides/list_message
        docs zh: https://www.coze.cn/docs/developer_guides/list_message

        :param conversation_id: The ID of the conversation.
        :param order: The sorting method for the message list.
        :param chat_id: The ID of the Chat.
        :param before_id: Get messages before the specified position.
        :param after_id: Get messages after the specified position.
        :param limit: The amount of data returned per query. Default is 50, with a range of 1 to 50.
        :return: The message list of the specified conversation.
        """
        url = f"{self._base_url}/v1/conversation/message/list"
        params = {
            "conversation_id": conversation_id,
        }

        async def request_maker(i_before_id: str, i_after_id: str) -> HTTPRequest:
            return await self._requester.amake_request(
                "POST",
                url,
                json={
                    "order": order,
                    "chat_id": chat_id,
                    "before_id": i_before_id if i_before_id else None,
                    "after_id": i_after_id if i_after_id else None,
                    "limit": limit,
                },
                params=params,
                cast=_PrivateListMessageResp,
                stream=False,
            )

        return await AsyncLastIDPaged.build(
            before_id=before_id or "",
            after_id=after_id or "",
            requestor=self._requester,
            request_maker=request_maker,
        )

    async def _list_page(
        self,
        *,
        conversation_id: str,
        order: Optional[str] = "desc",
        chat_id: Optional[str] = None,
        before_id: Optional[str] = None,
        after_id: Optional[str] = None,
        limit: Optional[int] = 50,
        **kwargs,
    ) -> _PrivateListMessageResp:
        """
        查看消息列表

        查看指定会话的消息列表。
        **查看消息列表** API 与**查看对话消息详情** API 的区别在于：
        * **查看消息列表** API 用于查询指定会话（conversation）中的消息记录，不仅包括开发者在会话中手动插入的每一条消息和用户发送的 Query，也包括调用**发起对话** API 得到的 type=answer 的智能体回复，但不包括 type=function_call、tool_response 和 follow-up 类型的对话中间态消息。
        * **查看对话消息详情** API 通常用于非流式对话场景中，查看某次对话（chat）中 type=answer 的智能体回复及 type=function_call、tool_response 和 follow-up 类型类型的对话中间态消息。不包括用户发送的 Query。
        消息在服务端的保存时长为180天，期满后，消息将自动从会话的消息记录中删除。

        :param conversation_id: Conversation ID，即会话的唯一标识。可以在[发起对话](https://www.coze.cn/docs/developer_guides/chat_v3)接口 Response 中查看 conversation_id 字段。
        :param order: 查询顺序  desc倒序 asc正序 TODO 默认倒序
        :param chat_id: 运行id
        :param before_id: 前序消息游标ID  已TODO str
        :param after_id: 后序消息游标ID  已TODO str
        :param limit: 每页限制条数  TODO 限制50条
        """
        url = f"{self._base_url}/v1/conversation/message/list"
        params = {
            "conversation_id": conversation_id,
        }
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "order": order,
            "chat_id": chat_id,
            "before_id": before_id if before_id else None,
            "after_id": after_id if after_id else None,
            "limit": limit,
        }
        return await self._requester.arequest(
            "post", url, False, cast=_PrivateListMessageResp, params=params, headers=headers, body=body
        )

    @property
    def feedback(self) -> "AsyncMessagesFeedbackClient":
        if not self._feedback:
            from .feedback import AsyncMessagesFeedbackClient

            self._feedback = AsyncMessagesFeedbackClient(self._base_url, self._requester)
        return self._feedback
