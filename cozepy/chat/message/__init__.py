from typing import Optional

from cozepy.chat import Message
from cozepy.model import ListResponse
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


class ChatMessagesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def list(
        self,
        *,
        conversation_id: str,
        chat_id: str,
        **kwargs,
    ) -> ListResponse[Message]:
        """
        查看对话消息详情

        调用此 API 之前，建议先以每秒最多 1 次的频率轮询 查看对话详情 API 确认本轮对话已结束（status=completed），否则调用此 API 时获取到的消息内容可能不完整。 查看指定对话中除 Query 以外的其他消息，包括模型回复、智能体执行的中间结果等消息。 接口描述 查看消息列表 API 与 查看对话消息详情 API 的区别在于： 查看消息列表 API 用于查询指定会话（conversation）中的消息记录，不仅包括开发者在会话中手动插入的每一条消息和用户发送的 Query，也包括调用 发起对话 API 得到的 type=answer 的智能体回复，但不包括 type=function_call、tool_response 和 follow-up 类型的对话中间态消息。 查看对话消息详情 API 通常用于非流式对话场景中，查看某次对话（chat）中 type=answer 的智能体回复及 type=function_call、tool_response 和 follow-up 类型类型的对话中间态消息。不包括用户发送的 Query。

        :param chat_id: Chat ID，即对话的唯一标识。可以在[发起对话](https://www.coze.cn/docs/developer_guides/chat_v3)接口 Response 中查看 id 字段，如果是流式响应，则在 Response 的 chat 事件中查看 id 字段。
        :param conversation_id: Conversation ID，即会话的唯一标识。可以在[发起对话](https://www.coze.cn/docs/developer_guides/chat_v3)接口 Response 中查看 conversation_id 字段。
        """
        url = f"{self._base_url}/v3/chat/message/list"
        params = {
            "conversation_id": conversation_id,
            "chat_id": chat_id,
        }
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("get", url, False, cast=ListResponse[Message], params=params, headers=headers)


class AsyncChatMessagesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def list(
        self,
        *,
        conversation_id: str,
        chat_id: str,
        **kwargs,
    ) -> ListResponse[Message]:
        """
        查看对话消息详情

        查看指定对话中除 Query 以外的其他消息，包括模型回复、智能体执行的中间结果等消息。 接口描述 查看消息列表 API 与 查看对话消息详情 API 的区别在于： 查看消息列表 API 用于查询指定会话（conversation）中的消息记录，不仅包括开发者在会话中手动插入的每一条消息和用户发送的 Query，也包括调用 发起对话 API 得到的 type=answer 的智能体回复，但不包括 type=function_call、tool_response 和 follow-up 类型的对话中间态消息。 查看对话消息详情 API 通常用于非流式对话场景中，查看某次对话（chat）中 type=answer 的智能体回复及 type=function_call、tool_response 和 follow-up 类型类型的对话中间态消息。不包括用户发送的 Query。 调用此 API 之前，建议先以每秒最多 1 次的频率轮询 查看对话详情 API 确认本轮对话已结束（status=completed），否则调用此 API 时获取到的消息内容可能不完整。

        :param chat_id: Chat ID，即对话的唯一标识。可以在[发起对话](https://www.coze.cn/docs/developer_guides/chat_v3)接口 Response 中查看 id 字段，如果是流式响应，则在 Response 的 chat 事件中查看 id 字段。
        :param conversation_id: Conversation ID，即会话的唯一标识。可以在[发起对话](https://www.coze.cn/docs/developer_guides/chat_v3)接口 Response 中查看 conversation_id 字段。
        """
        url = f"{self._base_url}/v3/chat/message/list"
        params = {
            "conversation_id": conversation_id,
            "chat_id": chat_id,
        }
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest(
            "get", url, False, cast=ListResponse[Message], params=params, headers=headers
        )
