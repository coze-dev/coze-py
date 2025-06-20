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

    @property
    def feedback(self) -> "ConversationsMessagesFeedbackClient":
        if not self._feedback:
            from .feedback import ConversationsMessagesFeedbackClient

            self._feedback = ConversationsMessagesFeedbackClient(self._base_url, self._requester)
        return self._feedback

    def create(
        self,
        *,
        conversation_id: str,
        role: MessageRole,
        content: str,
        content_type: MessageContentType,
        meta_data: Optional[Dict[str, str]] = None,
    ) -> Message:
        """
        Create a message and add it to the specified conversation.

        docs en: https://www.coze.com/docs/developer_guides/create_message
        docs cn: https://www.coze.cn/docs/developer_guides/create_message

        :param conversation_id: The ID of the conversation.
        :param role: The entity that sent this message.
        :param content: The content of the message, supporting pure text, multimodal (mixed input of text, images,
        files), cards, and various types of content.
        :param content_type: The type of message content.
        :param meta_data: Additional information when creating a message, and this additional information will also be
        returned when retrieving messages.
        :return:
        """
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

        return self._requester.request("post", url, False, Message, params=params, body=body)

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

    def retrieve(
        self,
        *,
        conversation_id: str,
        message_id: str,
    ) -> Message:
        """
        Get the detailed information of specified message.

        docs en: https://www.coze.com/docs/developer_guides/retrieve_message
        docs zh: https://www.coze.cn/docs/developer_guides/retrieve_message

        :param conversation_id: The ID of the conversation.
        :param message_id: The ID of the message.
        :return: The detailed information of specified message.
        """
        url = f"{self._base_url}/v1/conversation/message/retrieve"
        params = {
            "conversation_id": conversation_id,
            "message_id": message_id,
        }

        return self._requester.request("get", url, False, Message, params=params)

    def update(
        self,
        *,
        conversation_id: str,
        message_id: str,
        content: Optional[str] = None,
        content_type: Optional[MessageContentType] = None,
        meta_data: Optional[Dict[str, str]] = None,
    ) -> Message:
        """
        Modify a message, supporting the modification of message content, additional content, and message type.

        docs en: https://www.coze.com/docs/developer_guides/modify_message
        docs cn: https://www.coze.cn/docs/developer_guides/modify_message

        :param conversation_id: The ID of the conversation.
        :param message_id: The ID of the message.
        :param content: The content of the message, supporting pure text, multimodal (mixed input of text, images,
        files), cards, and various types of content.
        :param content_type: The type of message content.
        :param meta_data:
        :return: The detailed information of specified message.
        """
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

        return self._requester.request("post", url, False, Message, params=params, body=body, data_field="message")

    def delete(
        self,
        *,
        conversation_id: str,
        message_id: str,
    ) -> Message:
        """
        Call the API to delete a message within a specified conversation.

        docs en: https://www.coze.com/docs/developer_guides/delete_message
        docs zh: https://www.coze.cn/docs/developer_guides/delete_message

        :param conversation_id:
        :param message_id:
        :return:
        """
        url = f"{self._base_url}/v1/conversation/message/delete"
        params = {
            "conversation_id": conversation_id,
            "message_id": message_id,
        }

        return self._requester.request("post", url, False, Message, params=params)


class AsyncMessagesClient(object):
    """
    Message class.
    """

    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

        self._feedback: Optional["AsyncMessagesFeedbackClient"] = None

    @property
    def feedback(self) -> "AsyncMessagesFeedbackClient":
        if not self._feedback:
            from .feedback import AsyncMessagesFeedbackClient

            self._feedback = AsyncMessagesFeedbackClient(self._base_url, self._requester)
        return self._feedback

    async def create(
        self,
        *,
        conversation_id: str,
        role: MessageRole,
        content: str,
        content_type: MessageContentType,
        meta_data: Optional[Dict[str, str]] = None,
    ) -> Message:
        """
        Create a message and add it to the specified conversation.

        docs en: https://www.coze.com/docs/developer_guides/create_message
        docs cn: https://www.coze.cn/docs/developer_guides/create_message

        :param conversation_id: The ID of the conversation.
        :param role: The entity that sent this message.
        :param content: The content of the message, supporting pure text, multimodal (mixed input of text, images,
        files), cards, and various types of content.
        :param content_type: The type of message content.
        :param meta_data: Additional information when creating a message, and this additional information will also be
        returned when retrieving messages.
        :return:
        """
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

        return await self._requester.arequest("post", url, False, Message, params=params, body=body)

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

    async def retrieve(
        self,
        *,
        conversation_id: str,
        message_id: str,
    ) -> Message:
        """
        Get the detailed information of specified message.

        docs en: https://www.coze.com/docs/developer_guides/retrieve_message
        docs zh: https://www.coze.cn/docs/developer_guides/retrieve_message

        :param conversation_id: The ID of the conversation.
        :param message_id: The ID of the message.
        :return: The detailed information of specified message.
        """
        url = f"{self._base_url}/v1/conversation/message/retrieve"
        params = {
            "conversation_id": conversation_id,
            "message_id": message_id,
        }

        return await self._requester.arequest("get", url, False, Message, params=params)

    async def update(
        self,
        *,
        conversation_id: str,
        message_id: str,
        content: Optional[str] = None,
        content_type: Optional[MessageContentType] = None,
        meta_data: Optional[Dict[str, str]] = None,
    ) -> Message:
        """
        Modify a message, supporting the modification of message content, additional content, and message type.

        docs en: https://www.coze.com/docs/developer_guides/modify_message
        docs cn: https://www.coze.cn/docs/developer_guides/modify_message

        :param conversation_id: The ID of the conversation.
        :param message_id: The ID of the message.
        :param content: The content of the message, supporting pure text, multimodal (mixed input of text, images,
        files), cards, and various types of content.
        :param content_type: The type of message content.
        :param meta_data:
        :return: The detailed information of specified message.
        """
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

        return await self._requester.arequest(
            "post", url, False, Message, params=params, body=body, data_field="message"
        )

    async def delete(
        self,
        *,
        conversation_id: str,
        message_id: str,
    ) -> Message:
        """
        Call the API to delete a message within a specified conversation.

        docs en: https://www.coze.com/docs/developer_guides/delete_message
        docs zh: https://www.coze.cn/docs/developer_guides/delete_message

        :param conversation_id:
        :param message_id:
        :return:
        """
        url = f"{self._base_url}/v1/conversation/message/delete"
        params = {
            "conversation_id": conversation_id,
            "message_id": message_id,
        }

        return await self._requester.arequest("post", url, False, Message, params=params)
