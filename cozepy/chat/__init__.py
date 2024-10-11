from enum import Enum
from typing import TYPE_CHECKING, AsyncIterator, Dict, List, Optional, Union, overload

from typing_extensions import Literal

from cozepy.auth import Auth
from cozepy.exception import CozeAPIError
from cozepy.model import AsyncStream, CozeModel, Stream
from cozepy.request import Requester

if TYPE_CHECKING:
    from .message import AsyncChatMessagesClient, ChatMessagesClient


class MessageRole(str, Enum):
    # Indicates that the content of the message is sent by the user.
    USER = "user"

    # Indicates that the content of the message is sent by the bot.
    ASSISTANT = "assistant"


class MessageType(str, Enum):
    # User input content.
    # 用户输入内容。
    QUESTION = "question"

    # The message content returned by the Bot to the user, supporting incremental return. If the workflow is bound to a message node, there may be multiple answer scenarios, and the end flag of the streaming return can be used to determine that all answers are completed.
    # Bot 返回给用户的消息内容，支持增量返回。如果工作流绑定了消息节点，可能会存在多 answer 场景，此时可以用流式返回的结束标志来判断所有 answer 完成。
    ANSWER = "answer"

    # Intermediate results of the function (function call) called during the Bot conversation process.
    # Bot 对话过程中调用函数（function call）的中间结果。
    FUNCTION_CALL = "function_call"

    # Results returned after calling the tool (function call).
    # 调用工具 （function call）后返回的结果。
    TOOL_OUTPUT = "tool_output"

    # Results returned after calling the tool (function call).
    # 调用工具 （function call）后返回的结果。
    TOOL_RESPONSE = "tool_response"

    # If the user question suggestion switch is turned on in the Bot configuration, the reply content related to the recommended questions will be returned.
    # 如果在 Bot 上配置打开了用户问题建议开关，则会返回推荐问题相关的回复内容。不支持在请求中作为入参。
    FOLLOW_UP = "follow_up"

    # In the scenario of multiple answers, the server will return a verbose package, and the corresponding content is in JSON format. content.msg_type = generate_answer_finish represents that all answers have been replied to.
    # 多 answer 场景下，服务端会返回一个 verbose 包，对应的 content 为 JSON 格式，content.msg_type =generate_answer_finish 代表全部 answer 回复完成。不支持在请求中作为入参。
    VERBOSE = "verbose"

    UNKNOWN = ""


class MessageContentType(str, Enum):
    # Text.
    # 文本。
    TEXT = "text"

    # Multimodal content, that is, a combination of text and files, or a combination of text and images.
    # 多模态内容，即文本和文件的组合、文本和图片的组合。
    OBJECT_STRING = "object_string"

    # message card. This enum value only appears in the interface response and is not supported as an input parameter.
    # 卡片。此枚举值仅在接口响应中出现，不支持作为入参。
    CARD = "card"


class MessageObjectStringType(str, Enum):
    """
    The content type of the multimodal message.
    """

    TEXT = "text"
    FILE = "file"
    IMAGE = "image"


class MessageObjectString(CozeModel):
    # The content type of the multimodal message.
    # 多模态消息内容类型
    type: MessageObjectStringType
    # Text content. Required when type is text.
    # 文本内容。
    text: str
    # The ID of the file or image content.
    # 在 type 为 file 或 image 时，file_id 和 file_url 应至少指定一个。
    file_id: str
    # The online address of the file or image content.<br>Must be a valid address that is publicly accessible.
    # file_id or file_url must be specified when type is file or image.
    # 文件或图片内容的在线地址。必须是可公共访问的有效地址。
    # 在 type 为 file 或 image 时，file_id 和 file_url 应至少指定一个。
    file_url: str


class Message(CozeModel):
    # The entity that sent this message.
    role: MessageRole
    # The type of message.
    type: MessageType = MessageType.UNKNOWN
    # The content of the message. It supports various types of content, including plain text, multimodal (a mix of text, images, and files), message cards, and more.
    # 消息的内容，支持纯文本、多模态（文本、图片、文件混合输入）、卡片等多种类型的内容。
    content: str
    # The type of message content.
    # 消息内容的类型
    content_type: MessageContentType
    # Additional information when creating a message, and this additional information will also be returned when retrieving messages.
    # Custom key-value pairs should be specified in Map object format, with a length of 16 key-value pairs. The length of the key should be between 1 and 64 characters, and the length of the value should be between 1 and 512 characters.
    # 创建消息时的附加消息，获取消息时也会返回此附加消息。
    # 自定义键值对，应指定为 Map 对象格式。长度为 16 对键值对，其中键（key）的长度范围为 1～64 个字符，值（value）的长度范围为 1～512 个字符。
    meta_data: Optional[Dict[str, str]] = None

    id: Optional[str] = None
    conversation_id: Optional[str] = None
    bot_id: Optional[str] = None
    chat_id: Optional[str] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None

    @staticmethod
    def user_text_message(content: str, meta_data: Optional[Dict[str, str]] = None) -> "Message":
        return Message(
            role=MessageRole.USER,
            type=MessageType.QUESTION,
            content=content,
            content_type=MessageContentType.TEXT,
            meta_data=meta_data,
        )

    @staticmethod
    def assistant_text_message(content: str, meta_data: Optional[Dict[str, str]] = None) -> "Message":
        return Message(
            role=MessageRole.ASSISTANT,
            type=MessageType.ANSWER,
            content=content,
            content_type=MessageContentType.TEXT,
            meta_data=meta_data,
        )


class ChatStatus(str, Enum):
    """
    The running status of the session
    """

    # The session has been created.
    CREATED = "created"

    # The Bot is processing.
    IN_PROGRESS = "in_progress"

    # The Bot has finished processing, and the session has ended.
    COMPLETED = "completed"

    # The session has failed.
    FAILED = "failed"

    # The session is interrupted and requires further processing.
    REQUIRES_ACTION = "requires_action"


class ChatError(CozeModel):
    # The error code. An integer type. 0 indicates success, other values indicate failure.
    code: int
    # The error message. A string type.
    msg: str


class Chat(CozeModel):
    # The ID of the chat.
    id: str
    # The ID of the conversation.
    conversation_id: str
    # The ID of the bot.
    bot_id: str
    # Indicates the create time of the chat. The value format is Unix timestamp in seconds.
    created_at: Optional[int] = None
    # Indicates the end time of the chat. The value format is Unix timestamp in seconds.
    completed_at: Optional[int] = None
    # Indicates the failure time of the chat. The value format is Unix timestamp in seconds.
    failed_at: Optional[int] = None
    # Additional information when creating a message, and this additional information will also be returned when retrieving messages.
    # Custom key-value pairs should be specified in Map object format, with a length of 16 key-value pairs. The length of the key should be between 1 and 64 characters, and the length of the value should be between 1 and 512 characters.
    meta_data: Optional[Dict[str, str]] = None
    # When the chat encounters an exception, this field returns detailed error information, including:
    # Code: The error code. An integer type. 0 indicates success, other values indicate failure.
    # Msg: The error message. A string type.
    last_error: Optional[ChatError] = None
    # The running status of the session. The values are:
    # created: The session has been created.
    # in_progress: The Bot is processing.
    # completed: The Bot has finished processing, and the session has ended.
    # failed: The session has failed.
    # requires_action: The session is interrupted and requires further processing.
    status: ChatStatus

    # Details of the information needed for execution.


class ChatEventType(str, Enum):
    # Event for creating a conversation, indicating the start of the conversation.
    # 创建对话的事件，表示对话开始。
    CONVERSATION_CHAT_CREATED = "conversation.chat.created"

    # The server is processing the conversation.
    # 服务端正在处理对话。
    CONVERSATION_CHAT_IN_PROGRESS = "conversation.chat.in_progress"

    # Incremental message, usually an incremental message when type=answer.
    # 增量消息，通常是 type=answer 时的增量消息。
    CONVERSATION_MESSAGE_DELTA = "conversation.message.delta"

    # The message has been completely replied to. At this point, the streaming package contains the spliced results of all message.delta, and each message is in a completed state.
    # message 已回复完成。此时流式包中带有所有 message.delta 的拼接结果，且每个消息均为 completed 状态。
    CONVERSATION_MESSAGE_COMPLETED = "conversation.message.completed"

    # The conversation is completed.
    # 对话完成。
    CONVERSATION_CHAT_COMPLETED = "conversation.chat.completed"

    # This event is used to mark a failed conversation.
    # 此事件用于标识对话失败。
    CONVERSATION_CHAT_FAILED = "conversation.chat.failed"

    # The conversation is interrupted and requires the user to report the execution results of the tool.
    # 对话中断，需要使用方上报工具的执行结果。
    CONVERSATION_CHAT_REQUIRES_ACTION = "conversation.chat.requires_action"

    # Error events during the streaming response process. For detailed explanations of code and msg, please refer to Error codes.
    # 流式响应过程中的错误事件。关于 code 和 msg 的详细说明，可参考错误码。
    ERROR = "error"

    # The streaming response for this session ended normally.
    # 本次会话的流式返回正常结束。
    DONE = "done"


class ChatEvent(CozeModel):
    event: ChatEventType
    chat: Optional[Chat] = None
    message: Optional[Message] = None


def _chat_stream_handler(data: Dict, logid: str, is_async: bool = False) -> ChatEvent:
    event = data["event"]
    event_data = data["data"]  # type: str
    if event == ChatEventType.DONE:
        if is_async:
            raise StopAsyncIteration
        raise StopIteration
    elif event == ChatEventType.ERROR:
        raise Exception(f"error event: {event_data}")  # TODO: error struct format
    elif event in [
        ChatEventType.CONVERSATION_MESSAGE_DELTA,
        ChatEventType.CONVERSATION_MESSAGE_COMPLETED,
    ]:
        return ChatEvent(event=event, message=Message.model_validate_json(event_data))
    elif event in [
        ChatEventType.CONVERSATION_CHAT_CREATED,
        ChatEventType.CONVERSATION_CHAT_IN_PROGRESS,
        ChatEventType.CONVERSATION_CHAT_COMPLETED,
        ChatEventType.CONVERSATION_CHAT_FAILED,
        ChatEventType.CONVERSATION_CHAT_REQUIRES_ACTION,
    ]:
        chat = Chat.model_validate_json(event_data)
        if event == ChatEventType.CONVERSATION_CHAT_FAILED and chat.last_error and chat.last_error.code > 0:
            raise CozeAPIError(chat.last_error.code, chat.last_error.msg, logid)
        return ChatEvent(event=event, chat=chat)
    else:
        raise ValueError(f"invalid chat.event: {event}, {data}")


def _sync_chat_stream_handler(data: Dict, logid: str) -> ChatEvent:
    return _chat_stream_handler(data, logid=logid, is_async=False)


def _async_chat_stream_handler(data: Dict, logid: str) -> ChatEvent:
    return _chat_stream_handler(data, logid=logid, is_async=True)


class ToolOutput(CozeModel):
    # The ID for reporting the running results. You can get this ID under the tool_calls field in response of the Chat
    # API.
    tool_call_id: str

    # The execution result of the tool.
    output: str


class ChatClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester
        self._messages: Optional[ChatMessagesClient] = None

    def create(
        self,
        *,
        bot_id: str,
        user_id: str,
        conversation_id: Optional[str] = None,
        additional_messages: Optional[List[Message]] = None,
        custom_variables: Optional[Dict[str, str]] = None,
        auto_save_history: bool = True,
        meta_data: Optional[Dict[str, str]] = None,
    ) -> Chat:
        """
        Call the Chat API with non-streaming to send messages to a published Coze bot.

        docs en: https://www.coze.com/docs/developer_guides/chat_v3
        docs zh: https://www.coze.cn/docs/developer_guides/chat_v3

        :param bot_id: The ID of the bot that the API interacts with.
        :param user_id: The user who calls the API to chat with the bot.
        This parameter is defined, generated, and maintained by the user within their business system.
        :param conversation_id: Indicate which conversation the chat is taking place in.
        :param additional_messages: Additional information for the conversation. You can pass the user's query for this
        conversation through this field. The array length is limited to 100, meaning up to 100 messages can be input.
        :param custom_variables: The customized variable in a key-value pair.
        :param auto_save_history: Whether to automatically save the history of conversation records.
        :param meta_data: Additional information, typically used to encapsulate some business-related fields.
        :return: chat object
        """
        return self._create(
            bot_id=bot_id,
            user_id=user_id,
            stream=False,
            additional_messages=additional_messages,
            custom_variables=custom_variables,
            auto_save_history=auto_save_history,
            meta_data=meta_data,
            conversation_id=conversation_id,
        )

    def stream(
        self,
        *,
        bot_id: str,
        user_id: str,
        additional_messages: Optional[List[Message]] = None,
        custom_variables: Optional[Dict[str, str]] = None,
        auto_save_history: bool = True,
        meta_data: Optional[Dict[str, str]] = None,
        conversation_id: Optional[str] = None,
    ) -> Stream[ChatEvent]:
        """
        Call the Chat API with streaming to send messages to a published Coze bot.

        docs en: https://www.coze.com/docs/developer_guides/chat_v3
        docs zh: https://www.coze.cn/docs/developer_guides/chat_v3

        :param bot_id: The ID of the bot that the API interacts with.
        :param user_id: The user who calls the API to chat with the bot.
        This parameter is defined, generated, and maintained by the user within their business system.
        :param conversation_id: Indicate which conversation the chat is taking place in.
        :param additional_messages: Additional information for the conversation. You can pass the user's query for this
        conversation through this field. The array length is limited to 100, meaning up to 100 messages can be input.
        :param custom_variables: The customized variable in a key-value pair.
        :param auto_save_history: Whether to automatically save the history of conversation records.
        :param meta_data: Additional information, typically used to encapsulate some business-related fields.
        :return: iterator of ChatEvent
        """
        return self._create(
            bot_id=bot_id,
            user_id=user_id,
            stream=True,
            additional_messages=additional_messages,
            custom_variables=custom_variables,
            auto_save_history=auto_save_history,
            meta_data=meta_data,
            conversation_id=conversation_id,
        )

    @overload
    def _create(
        self,
        *,
        bot_id: str,
        user_id: str,
        stream: Literal[True],
        additional_messages: Optional[List[Message]] = ...,
        custom_variables: Optional[Dict[str, str]] = ...,
        auto_save_history: bool = ...,
        meta_data: Optional[Dict[str, str]] = ...,
        conversation_id: Optional[str] = ...,
    ) -> Stream[ChatEvent]: ...

    @overload
    def _create(
        self,
        *,
        bot_id: str,
        user_id: str,
        stream: Literal[False],
        additional_messages: Optional[List[Message]] = ...,
        custom_variables: Optional[Dict[str, str]] = ...,
        auto_save_history: bool = ...,
        meta_data: Optional[Dict[str, str]] = ...,
        conversation_id: Optional[str] = ...,
    ) -> Chat: ...

    def _create(
        self,
        *,
        bot_id: str,
        user_id: str,
        stream: Literal[True, False],
        additional_messages: Optional[List[Message]] = None,
        custom_variables: Optional[Dict[str, str]] = None,
        auto_save_history: bool = True,
        meta_data: Optional[Dict[str, str]] = None,
        conversation_id: Optional[str] = None,
    ) -> Union[Chat, Stream[ChatEvent]]:
        """
        Create a conversation.
        Conversation is an interaction between a bot and a user, including one or more messages.
        """
        url = f"{self._base_url}/v3/chat"
        body = {
            "bot_id": bot_id,
            "user_id": user_id,
            "additional_messages": [i.model_dump() for i in additional_messages] if additional_messages else [],
            "stream": stream,
            "custom_variables": custom_variables,
            "auto_save_history": auto_save_history,
            "conversation_id": conversation_id if conversation_id else None,
            "meta_data": meta_data,
        }
        if not stream:
            return self._requester.request(
                "post",
                url,
                False,
                Chat,
                body=body,
            )

        steam_iters, logid = self._requester.request(
            "post",
            url,
            True,
            None,
            body=body,
        )
        return Stream(steam_iters, fields=["event", "data"], handler=_sync_chat_stream_handler, logid=logid)

    def retrieve(
        self,
        *,
        conversation_id: str,
        chat_id: str,
    ) -> Chat:
        """
        Get the detailed information of the chat.

        docs en: https://www.coze.com/docs/developer_guides/retrieve_chat
        docs zh: https://www.coze.cn/docs/developer_guides/retrieve_chat

        :param conversation_id: The ID of the conversation.
        :param chat_id: The ID of the chat.
        :return: chat object
        """
        url = f"{self._base_url}/v3/chat/retrieve"
        params = {
            "conversation_id": conversation_id,
            "chat_id": chat_id,
        }
        return self._requester.request("post", url, False, Chat, params=params)

    def submit_tool_outputs(
        self, *, conversation_id: str, chat_id: str, tool_outputs: List[ToolOutput], stream: bool
    ) -> Union[Chat, Stream[ChatEvent]]:
        """
        Call this API to submit the results of tool execution.

        docs en: https://www.coze.com/docs/developer_guides/chat_submit_tool_outputs
        docs zh: https://www.coze.cn/docs/developer_guides/chat_submit_tool_outputs

        :param conversation_id: The Conversation ID can be viewed in the 'conversation_id' field of the Response when
        initiating a conversation through the Chat API.
        :param chat_id: The Chat ID can be viewed in the 'id' field of the Response when initiating a chat through the
        Chat API. If it is a streaming response, check the 'id' field in the chat event of the Response.
        :param tool_outputs: The execution result of the tool. For detailed instructions, refer to the ToolOutput Object
        :param stream: Whether to enable streaming response.
        true: Fill in the context of the previous conversation and continue with streaming response.
        false: (Default) Non-streaming response, only reply with basic information of the conversation.
        :return:
        """
        url = f"{self._base_url}/v3/chat/submit_tool_outputs"
        params = {
            "conversation_id": conversation_id,
            "chat_id": chat_id,
        }
        body = {
            "tool_outputs": [i.model_dump() for i in tool_outputs],
            "stream": stream,
        }

        if not stream:
            return self._requester.request(
                "post",
                url,
                False,
                Chat,
                params=params,
                body=body,
            )

        steam_iters, logid = self._requester.request(
            "post",
            url,
            True,
            None,
            params=params,
            body=body,
        )
        return Stream(steam_iters, fields=["event", "data"], handler=_sync_chat_stream_handler, logid=logid)

    def cancel(
        self,
        *,
        conversation_id: str,
        chat_id: str,
    ) -> Chat:
        """
        Call this API to cancel an ongoing chat.

        docs en: https://www.coze.com/docs/developer_guides/chat_cancel
        docs zh: https://www.coze.cn/docs/developer_guides/chat_cancel

        :param conversation_id: The Conversation ID can be viewed in the 'conversation_id' field of the Response when
        initiating a conversation through the Chat API.
        :param chat_id: The Chat ID can be viewed in the 'id' field of the Response when initiating a chat through the
        Chat API. If it is a streaming response, check the 'id' field in the chat event of the Response.
        :return:
        """
        url = f"{self._base_url}/v3/chat/cancel"
        params = {
            "conversation_id": conversation_id,
            "chat_id": chat_id,
        }
        return self._requester.request("post", url, False, Chat, params=params)

    @property
    def messages(
        self,
    ) -> "ChatMessagesClient":
        if self._messages is None:
            from .message import ChatMessagesClient

            self._messages = ChatMessagesClient(self._base_url, self._auth, self._requester)
        return self._messages


class AsyncChatClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester
        self._messages: Optional[AsyncChatMessagesClient] = None

    async def create(
        self,
        *,
        bot_id: str,
        user_id: str,
        conversation_id: Optional[str] = None,
        additional_messages: Optional[List[Message]] = None,
        custom_variables: Optional[Dict[str, str]] = None,
        auto_save_history: bool = True,
        meta_data: Optional[Dict[str, str]] = None,
    ) -> Chat:
        """
        Call the Chat API with non-streaming to send messages to a published Coze bot.

        docs en: https://www.coze.com/docs/developer_guides/chat_v3
        docs zh: https://www.coze.cn/docs/developer_guides/chat_v3

        :param bot_id: The ID of the bot that the API interacts with.
        :param user_id: The user who calls the API to chat with the bot.
        This parameter is defined, generated, and maintained by the user within their business system.
        :param conversation_id: Indicate which conversation the chat is taking place in.
        :param additional_messages: Additional information for the conversation. You can pass the user's query for this
        conversation through this field. The array length is limited to 100, meaning up to 100 messages can be input.
        :param custom_variables: The customized variable in a key-value pair.
        :param auto_save_history: Whether to automatically save the history of conversation records.
        :param meta_data: Additional information, typically used to encapsulate some business-related fields.
        :return: chat object
        """
        return await self._create(
            bot_id=bot_id,
            user_id=user_id,
            additional_messages=additional_messages,
            stream=False,
            custom_variables=custom_variables,
            auto_save_history=auto_save_history,
            meta_data=meta_data,
            conversation_id=conversation_id,
        )

    async def stream(
        self,
        *,
        bot_id: str,
        user_id: str,
        additional_messages: Optional[List[Message]] = None,
        custom_variables: Optional[Dict[str, str]] = None,
        auto_save_history: bool = True,
        meta_data: Optional[Dict[str, str]] = None,
        conversation_id: Optional[str] = None,
    ) -> AsyncIterator[ChatEvent]:
        """
        Call the Chat API with streaming to send messages to a published Coze bot.

        docs en: https://www.coze.com/docs/developer_guides/chat_v3
        docs zh: https://www.coze.cn/docs/developer_guides/chat_v3

        :param bot_id: The ID of the bot that the API interacts with.
        :param user_id: The user who calls the API to chat with the bot.
        This parameter is defined, generated, and maintained by the user within their business system.
        :param conversation_id: Indicate which conversation the chat is taking place in.
        :param additional_messages: Additional information for the conversation. You can pass the user's query for this
        conversation through this field. The array length is limited to 100, meaning up to 100 messages can be input.
        :param custom_variables: The customized variable in a key-value pair.
        :param auto_save_history: Whether to automatically save the history of conversation records.
        :param meta_data: Additional information, typically used to encapsulate some business-related fields.
        :return: iterator of ChatEvent
        """
        async for item in await self._create(
            bot_id=bot_id,
            user_id=user_id,
            additional_messages=additional_messages,
            stream=True,
            custom_variables=custom_variables,
            auto_save_history=auto_save_history,
            meta_data=meta_data,
            conversation_id=conversation_id,
        ):
            yield item

    @overload
    async def _create(
        self,
        *,
        bot_id: str,
        user_id: str,
        stream: Literal[True],
        additional_messages: Optional[List[Message]] = ...,
        custom_variables: Optional[Dict[str, str]] = ...,
        auto_save_history: bool = ...,
        meta_data: Optional[Dict[str, str]] = ...,
        conversation_id: Optional[str] = ...,
    ) -> AsyncStream[ChatEvent]: ...

    @overload
    async def _create(
        self,
        *,
        bot_id: str,
        user_id: str,
        stream: Literal[False],
        additional_messages: Optional[List[Message]] = ...,
        custom_variables: Optional[Dict[str, str]] = ...,
        auto_save_history: bool = ...,
        meta_data: Optional[Dict[str, str]] = ...,
        conversation_id: Optional[str] = ...,
    ) -> Chat: ...

    async def _create(
        self,
        *,
        bot_id: str,
        user_id: str,
        stream: Literal[True, False],
        additional_messages: Optional[List[Message]] = None,
        custom_variables: Optional[Dict[str, str]] = None,
        auto_save_history: bool = True,
        meta_data: Optional[Dict[str, str]] = None,
        conversation_id: Optional[str] = None,
    ) -> Union[Chat, AsyncStream[ChatEvent]]:
        """
        Create a conversation.
        Conversation is an interaction between a bot and a user, including one or more messages.
        """
        url = f"{self._base_url}/v3/chat"
        body = {
            "bot_id": bot_id,
            "user_id": user_id,
            "additional_messages": [i.model_dump() for i in additional_messages] if additional_messages else [],
            "stream": stream,
            "custom_variables": custom_variables,
            "auto_save_history": auto_save_history,
            "conversation_id": conversation_id if conversation_id else None,
            "meta_data": meta_data,
        }
        if not stream:
            return await self._requester.arequest(
                "post",
                url,
                False,
                Chat,
                body=body,
            )

        steam_iters, logid = await self._requester.arequest(
            "post",
            url,
            True,
            None,
            body=body,
        )
        return AsyncStream(steam_iters, fields=["event", "data"], handler=_async_chat_stream_handler, logid=logid)

    async def retrieve(
        self,
        *,
        conversation_id: str,
        chat_id: str,
    ) -> Chat:
        """
        Get the detailed information of the chat.

        docs en: https://www.coze.com/docs/developer_guides/retrieve_chat
        docs zh: https://www.coze.cn/docs/developer_guides/retrieve_chat

        :param conversation_id: The ID of the conversation.
        :param chat_id: The ID of the chat.
        :return: chat object
        """
        url = f"{self._base_url}/v3/chat/retrieve"
        params = {
            "conversation_id": conversation_id,
            "chat_id": chat_id,
        }
        return await self._requester.arequest("post", url, False, Chat, params=params)

    async def submit_tool_outputs(self, *, conversation_id: str, chat_id: str, tool_outputs: List[ToolOutput]) -> Chat:
        """
        Call this API to submit the results of tool execution.

        docs en: https://www.coze.com/docs/developer_guides/chat_submit_tool_outputs
        docs zh: https://www.coze.cn/docs/developer_guides/chat_submit_tool_outputs

        :param conversation_id: The Conversation ID can be viewed in the 'conversation_id' field of the Response when
        initiating a conversation through the Chat API.
        :param chat_id: The Chat ID can be viewed in the 'id' field of the Response when initiating a chat through the
        Chat API. If it is a streaming response, check the 'id' field in the chat event of the Response.
        :param tool_outputs: The execution result of the tool. For detailed instructions, refer to the ToolOutput Object
        true: Fill in the context of the previous conversation and continue with streaming response.
        false: (Default) Non-streaming response, only reply with basic information of the conversation.
        :return:
        """

        return await self._submit_tool_outputs(
            conversation_id=conversation_id, chat_id=chat_id, stream=False, tool_outputs=tool_outputs
        )

    async def submit_tool_outputs_stream(
        self,
        *,
        conversation_id: str,
        chat_id: str,
        tool_outputs: List[ToolOutput],
    ) -> AsyncIterator[ChatEvent]:
        """
        Call this API to submit the results of tool execution.

        docs en: https://www.coze.com/docs/developer_guides/chat_submit_tool_outputs
        docs zh: https://www.coze.cn/docs/developer_guides/chat_submit_tool_outputs

        :param conversation_id: The Conversation ID can be viewed in the 'conversation_id' field of the Response when
        initiating a conversation through the Chat API.
        :param chat_id: The Chat ID can be viewed in the 'id' field of the Response when initiating a chat through the
        Chat API. If it is a streaming response, check the 'id' field in the chat event of the Response.
        :param tool_outputs: The execution result of the tool. For detailed instructions, refer to the ToolOutput Object
        true: Fill in the context of the previous conversation and continue with streaming response.
        false: (Default) Non-streaming response, only reply with basic information of the conversation.
        :return:
        """

        async for item in await self._submit_tool_outputs(
            conversation_id=conversation_id, chat_id=chat_id, stream=True, tool_outputs=tool_outputs
        ):
            yield item

    @overload
    async def _submit_tool_outputs(
        self, *, conversation_id: str, chat_id: str, stream: Literal[True], tool_outputs: List[ToolOutput]
    ) -> AsyncStream[ChatEvent]: ...

    @overload
    async def _submit_tool_outputs(
        self, *, conversation_id: str, chat_id: str, stream: Literal[False], tool_outputs: List[ToolOutput]
    ) -> Chat: ...

    async def _submit_tool_outputs(
        self, *, conversation_id: str, chat_id: str, stream: Literal[True, False], tool_outputs: List[ToolOutput]
    ) -> Union[Chat, AsyncStream[ChatEvent]]:
        url = f"{self._base_url}/v3/chat/submit_tool_outputs"
        params = {
            "conversation_id": conversation_id,
            "chat_id": chat_id,
        }
        body = {
            "tool_outputs": [i.model_dump() for i in tool_outputs],
            "stream": stream,
        }

        if not stream:
            return await self._requester.arequest("post", url, False, Chat, params=params, body=body)

        steam_iters, logid = await self._requester.arequest("post", url, True, None, params=params, body=body)
        return AsyncStream(steam_iters, fields=["event", "data"], handler=_async_chat_stream_handler, logid=logid)

    async def cancel(
        self,
        *,
        conversation_id: str,
        chat_id: str,
    ) -> Chat:
        """
        Call this API to cancel an ongoing chat.

        docs en: https://www.coze.com/docs/developer_guides/chat_cancel
        docs zh: https://www.coze.cn/docs/developer_guides/chat_cancel

        :param conversation_id: The Conversation ID can be viewed in the 'conversation_id' field of the Response when
        initiating a conversation through the Chat API.
        :param chat_id: The Chat ID can be viewed in the 'id' field of the Response when initiating a chat through the
        Chat API. If it is a streaming response, check the 'id' field in the chat event of the Response.
        :return:
        """
        url = f"{self._base_url}/v3/chat/cancel"
        params = {
            "conversation_id": conversation_id,
            "chat_id": chat_id,
        }
        return await self._requester.arequest("post", url, False, Chat, params=params)

    @property
    def messages(
        self,
    ) -> "AsyncChatMessagesClient":
        if self._messages is None:
            from .message import AsyncChatMessagesClient

            self._messages = AsyncChatMessagesClient(self._base_url, self._auth, self._requester)
        return self._messages
