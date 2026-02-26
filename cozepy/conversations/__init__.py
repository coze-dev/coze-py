from typing import TYPE_CHECKING, Dict, List, Optional

from cozepy.chat import Message
from cozepy.model import AsyncNumberPaged, CozeModel, HTTPRequest, NumberPaged, NumberPagedResponse
from cozepy.request import Requester
from cozepy.util import dump_exclude_none, remove_url_trailing_slash

if TYPE_CHECKING:
    from cozepy.conversations.message import AsyncMessagesClient, MessagesClient


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


class _PrivateListConversationResp(CozeModel, NumberPagedResponse[Conversation]):
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
        self._messages: Optional[MessagesClient] = None

    @property
    def messages(self) -> "MessagesClient":
        if not self._messages:
            from .message import MessagesClient

            self._messages = MessagesClient(base_url=self._base_url, requester=self._requester)
        return self._messages

    def create(
        self,
        *,
        messages: Optional[List[Message]] = None,
        meta_data: Optional[Dict[str, str]] = None,
        bot_id: Optional[str] = None,
        name: Optional[str] = None,
        connector_id: Optional[str] = None,
        **kwargs,
    ) -> Conversation:
        """
        创建会话

        创建一个会话。
        接口描述
        会话是智能体和用户之间的基于一个或多个主题的问答交互，一个会话包含一条或多条消息。创建会话时，扣子会同时在会话中创建一个空白的上下文片段，用于存储某个主题的消息。后续发起对话时，上下文片段中的消息是模型可见的消息历史。
        你可以在创建会话时同步写入消息，或者创建会话后另外调用 创建消息 API 写入消息。消息默认写入到最新的一个上下文片段中，对话时将作为上下文传递给模型。
        会话、对话、消息和上下文片段的概念说明，可参考基础概念。
        如果需要将不同业务侧用户的会话互相隔离，请参见如何实现会话隔离。

        :param messages: 校验最多16个
        """
        url = f"{self._base_url}/v1/conversation/create"
        headers: Optional[dict] = kwargs.get("headers")
        body = dump_exclude_none(
            {
                "messages": messages,
                "meta_data": meta_data,
                "bot_id": bot_id,
                "name": name,
                "connector_id": connector_id,
            }
        )
        return self._requester.request("post", url, False, cast=Conversation, headers=headers, body=body)

    def retrieve(self, *, conversation_id: str, **kwargs) -> Conversation:
        """
        查看会话消息

        通过会话 ID 查看会话信息。
        接口限制
        仅支持查询本人创建的会话。

        :param conversation_id: Conversation ID，用于查询指定会话的详细信息。你可以在[发起对话](https://www.coze.cn/docs/developer_guides/chat_v3)接口的 Response 中通过 `conversation_id` 字段获取会话 ID。
        """
        url = f"{self._base_url}/v1/conversation/retrieve"
        params = {
            "conversation_id": conversation_id,
        }
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("get", url, False, cast=Conversation, params=params, headers=headers)

    def update(self, *, conversation_id: str, name: Optional[str] = None, **kwargs) -> Conversation:
        """
        更新会话名称

        会话创建者可以更新指定会话的会话名，以便更好地识别和管理会话。
        在创建会话时，扣子会默认将用户发送的第一个消息内容作为会话名称。用户也可以根据会话的实际内容或主题对会话名称进行更新，从而更直观地区分不同的会话，提升管理效率。

        :param conversation_id: 待更新的会话 ID。你可以在[发起对话](https://www.coze.cn/docs/developer_guides/chat_v3)接口的 Response 中通过 `conversation_id` 字段获取会话 ID。
        """
        url = f"{self._base_url}/v1/conversations/{conversation_id}"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "name": name,
        }
        return self._requester.request("put", url, False, cast=Conversation, headers=headers, body=body)

    def delete(self, *, conversation_id: str, **kwargs) -> DeleteConversationResp:
        """
        删除指定的会话。
        删除后会话及其中的所有消息都将被永久删除，无法恢复。

        docs: https://www.coze.cn/docs/developer_guides/delete_conversation

        :param conversation_id: 要删除的会话ID
        :return: DeleteConversationResp对象表示删除成功
        """
        url = f"{self._base_url}/v1/conversations/{conversation_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("delete", url, False, cast=DeleteConversationResp, headers=headers)

    def list(
        self,
        *,
        bot_id: str,
        page_num: int = 1,
        page_size: int = 50,
        **kwargs,
    ) -> NumberPaged[Conversation]:
        """
        查看会话列表

        查看指定智能体的会话列表。
        调用此 API 之前，应确认当前使用的访问密钥拥有智能体所在工作空间的权限。
        仅支持通过此 API 查看智能体在 API 或 Chat SDK 渠道产生的会话。
        仅支持查询本人创建的会话。

        :param bot_id: 智能体 ID，获取方法如下： 进入智能体的 开发页面，开发页面 URL 中 `bot` 参数后的数字就是智能体 ID。例如`https://www.coze.cn/space/341****/bot/73428668*****`，智能体 ID 为`73428668*****`。
        :param connector_id: 发布渠道 ID，用于筛选指定渠道的会话。仅支持查看以下渠道的会话： * （默认）API 渠道，渠道 ID 为 1024。 * Chat SDK 渠道，渠道 ID 为 999。
        :param page_num: 页码，从 1 开始，默认为 1。
        :param page_size: 每一页的数据条目个数，默认为 50，最大为 50。
        :param sort_order: 会话列表的排序方式： * **ASC**：按创建时间升序排序，最早创建的会话排序最前。 * **DESC**：（默认）按创建时间降序排序，最近创建的会话排序最前。
        """
        url = f"{self._base_url}/v1/conversations"
        headers: Optional[dict] = kwargs.get("headers")

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                headers=headers,
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

    def clear(self, *, conversation_id: str, **kwargs) -> Section:
        """
        清除上下文

        清除指定会话中的上下文。
        <span id="3a1c8d70"></span>
        ## 接口说明
        在智能体对话场景中，上下文指模型在处理当前输入时所能参考的历史消息、对话记录，它决定了模型对当前任务的理解深度和连贯性，直接影响输出结果的准确性和相关性。多轮对话中，如果需要开启新的话题，可以调用此 API 清除上下文。清除上下文后，对话中的历史消息不会作为上下文被输入给模型，后续对话不再受之前历史消息的影响，避免信息干扰，确保对话的准确性和连贯性。
        会话中的消息存储在上下文段落（section）中，每次调用此 API 清除上下文时，系统会自动删除旧的上下文段落，并创建新的上下文段落用于存储新的消息。再次发起对话时，新分区中的消息会作为新的上下文传递给模型参考。
        * 清除上下文 API 只是清空模型可见的消息历史，不会实际删除会话中的消息，通过[查看消息列表](https://www.coze.cn/open/docs/developer_guides/list_message)或[查看消息详情](https://www.coze.cn/open/docs/developer_guides/retrieve_message)等 API 仍能查看到消息内容。
        * 会话、对话、消息和上下文段落的术语解释请参见[基础概念](https://www.coze.cn/open/docs/developer_guides/coze_api_overview#fed4a54c)。
        ![图片](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/e4b55816254c4446ae59bbca33ca8e1d~tplv-goo7wpa0wc-image.image)

        :param conversation_id: 待清除上下文的会话 ID。你可以在[发起对话](https://www.coze.cn/docs/developer_guides/chat_v3)接口的 Response 中通过 conversation_id 字段获取会话 ID。
        """
        url = f"{self._base_url}/v1/conversations/{conversation_id}/clear"
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("post", url, False, cast=Section, headers=headers)


class AsyncConversationsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._messages: Optional[AsyncMessagesClient] = None

    @property
    def messages(self) -> "AsyncMessagesClient":
        if not self._messages:
            from .message import AsyncMessagesClient

            self._messages = AsyncMessagesClient(base_url=self._base_url, requester=self._requester)
        return self._messages

    async def create(
        self,
        *,
        messages: Optional[List[Message]] = None,
        meta_data: Optional[Dict[str, str]] = None,
        bot_id: Optional[str] = None,
        name: Optional[str] = None,
        connector_id: Optional[str] = None,
        **kwargs,
    ) -> Conversation:
        """
        创建会话

        创建一个会话。
        接口描述
        会话是智能体和用户之间的基于一个或多个主题的问答交互，一个会话包含一条或多条消息。创建会话时，扣子会同时在会话中创建一个空白的上下文片段，用于存储某个主题的消息。后续发起对话时，上下文片段中的消息是模型可见的消息历史。
        你可以在创建会话时同步写入消息，或者创建会话后另外调用 创建消息 API 写入消息。消息默认写入到最新的一个上下文片段中，对话时将作为上下文传递给模型。
        会话、对话、消息和上下文片段的概念说明，可参考基础概念。
        如果需要将不同业务侧用户的会话互相隔离，请参见如何实现会话隔离。

        :param messages: 校验最多16个
        """
        url = f"{self._base_url}/v1/conversation/create"
        headers: Optional[dict] = kwargs.get("headers")
        body = dump_exclude_none(
            {
                "messages": messages,
                "meta_data": meta_data,
                "bot_id": bot_id,
                "name": name,
                "connector_id": connector_id,
            }
        )
        return await self._requester.arequest("post", url, False, cast=Conversation, headers=headers, body=body)

    async def retrieve(self, *, conversation_id: str, **kwargs) -> Conversation:
        """
        查看会话消息

        通过会话 ID 查看会话信息。
        接口限制
        仅支持查询本人创建的会话。

        :param conversation_id: Conversation ID，用于查询指定会话的详细信息。你可以在[发起对话](https://www.coze.cn/docs/developer_guides/chat_v3)接口的 Response 中通过 `conversation_id` 字段获取会话 ID。
        """
        url = f"{self._base_url}/v1/conversation/retrieve"
        params = {
            "conversation_id": conversation_id,
        }
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest("get", url, False, cast=Conversation, params=params, headers=headers)

    async def update(self, *, conversation_id: str, name: Optional[str] = None, **kwargs) -> Conversation:
        """
        更新会话名称

        会话创建者可以更新指定会话的会话名，以便更好地识别和管理会话。
        在创建会话时，扣子会默认将用户发送的第一个消息内容作为会话名称。用户也可以根据会话的实际内容或主题对会话名称进行更新，从而更直观地区分不同的会话，提升管理效率。

        :param conversation_id: 待更新的会话 ID。你可以在[发起对话](https://www.coze.cn/docs/developer_guides/chat_v3)接口的 Response 中通过 `conversation_id` 字段获取会话 ID。
        """
        url = f"{self._base_url}/v1/conversations/{conversation_id}"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "name": name,
        }
        return await self._requester.arequest("put", url, False, cast=Conversation, headers=headers, body=body)

    async def delete(self, *, conversation_id: str, **kwargs) -> DeleteConversationResp:
        """
        删除指定的会话。
        删除后会话及其中的所有消息都将被永久删除，无法恢复。

        docs: https://www.coze.cn/docs/developer_guides/delete_conversation

        :param conversation_id: 要删除的会话ID
        :return: DeleteConversationResp对象表示删除成功
        """
        url = f"{self._base_url}/v1/conversations/{conversation_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest("delete", url, False, cast=DeleteConversationResp, headers=headers)

    async def list(
        self,
        *,
        bot_id: str,
        page_num: int = 1,
        page_size: int = 50,
        **kwargs,
    ) -> AsyncNumberPaged[Conversation]:
        """
        查看会话列表
        调用此 API 之前，应确认当前使用的访问密钥拥有智能体所在工作空间的权限。
        仅支持通过此 API 查看智能体在 API 或 Chat SDK 渠道产生的会话。
        仅支持查询本人创建的会话。
        查看指定智能体的会话列表。
        :param bot_id: 智能体 ID，获取方法如下： 进入智能体的 开发页面，开发页面 URL 中 `bot` 参数后的数字就是智能体 ID。例如`https://www.coze.cn/space/341****/bot/73428668*****`，智能体 ID 为`73428668*****`。
        :param connector_id: 发布渠道 ID，用于筛选指定渠道的会话。
        仅支持查看以下渠道的会话： * （默认）API 渠道，渠道 ID 为 1024。
        * Chat SDK 渠道，渠道 ID 为 999。
        :param page_num: 页码，从 1 开始，默认为 1。
        :param page_size: 每一页的数据条目个数，默认为 50，最大为 50。
        :param sort_order: 会话列表的排序方式： * **ASC**：按创建时间升序排序，最早创建的会话排序最前。
        * **DESC**：（默认）按创建时间降序排序，最近创建的会话排序最前。
        """
        url = f"{self._base_url}/v1/conversations"
        headers: Optional[dict] = kwargs.get("headers")

        async def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "GET",
                url,
                headers=headers,
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

    async def clear(self, *, conversation_id: str, **kwargs) -> Section:
        """
        清除上下文

        清除指定会话中的上下文。
        <span id="3a1c8d70"></span>
        ## 接口说明
        在智能体对话场景中，上下文指模型在处理当前输入时所能参考的历史消息、对话记录，它决定了模型对当前任务的理解深度和连贯性，直接影响输出结果的准确性和相关性。多轮对话中，如果需要开启新的话题，可以调用此 API 清除上下文。清除上下文后，对话中的历史消息不会作为上下文被输入给模型，后续对话不再受之前历史消息的影响，避免信息干扰，确保对话的准确性和连贯性。
        会话中的消息存储在上下文段落（section）中，每次调用此 API 清除上下文时，系统会自动删除旧的上下文段落，并创建新的上下文段落用于存储新的消息。再次发起对话时，新分区中的消息会作为新的上下文传递给模型参考。
        * 清除上下文 API 只是清空模型可见的消息历史，不会实际删除会话中的消息，通过[查看消息列表](https://www.coze.cn/open/docs/developer_guides/list_message)或[查看消息详情](https://www.coze.cn/open/docs/developer_guides/retrieve_message)等 API 仍能查看到消息内容。
        * 会话、对话、消息和上下文段落的术语解释请参见[基础概念](https://www.coze.cn/open/docs/developer_guides/coze_api_overview#fed4a54c)。
        ![图片](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/e4b55816254c4446ae59bbca33ca8e1d~tplv-goo7wpa0wc-image.image)

        :param conversation_id: 待清除上下文的会话 ID。你可以在[发起对话](https://www.coze.cn/docs/developer_guides/chat_v3)接口的 Response 中通过 conversation_id 字段获取会话 ID。
        """
        url = f"{self._base_url}/v1/conversations/{conversation_id}/clear"
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest("post", url, False, cast=Section, headers=headers)
