from enum import StrEnum, Enum
from typing import Dict, List, Optional

from .auth import Auth
from .model import CozeModel
from .request import Requester


class MessageRole(str, Enum):
    # Indicates that the content of the message is sent by the user.
    user = "user"
    # Indicates that the content of the message is sent by the bot.
    assistant = "assistant"


class MessageType(StrEnum):
    # User input content.
    # 用户输入内容。
    question = "question"
    # The message content returned by the Bot to the user, supporting incremental return. If the workflow is bound to a message node, there may be multiple answer scenarios, and the end flag of the streaming return can be used to determine that all answers are completed.
    # Bot 返回给用户的消息内容，支持增量返回。如果工作流绑定了消息节点，可能会存在多 answer 场景，此时可以用流式返回的结束标志来判断所有 answer 完成。
    answer = "answer"
    # Intermediate results of the function (function call) called during the Bot conversation process.
    # Bot 对话过程中调用函数（function call）的中间结果。
    function_call = "function_call"
    # Results returned after calling the tool (function call).
    # 调用工具 （function call）后返回的结果。
    tool_output = "tool_output"
    # Results returned after calling the tool (function call).
    # 调用工具 （function call）后返回的结果。
    tool_response = "tool_response"
    # If the user question suggestion switch is turned on in the Bot configuration, the reply content related to the recommended questions will be returned.
    # 如果在 Bot 上配置打开了用户问题建议开关，则会返回推荐问题相关的回复内容。不支持在请求中作为入参。
    follow_up = "follow_up"
    # In the scenario of multiple answers, the server will return a verbose package, and the corresponding content is in JSON format. content.msg_type = generate_answer_finish represents that all answers have been replied to.
    # 多 answer 场景下，服务端会返回一个 verbose 包，对应的 content 为 JSON 格式，content.msg_type =generate_answer_finish 代表全部 answer 回复完成。不支持在请求中作为入参。
    verbose = "verbose"


class MessageContentType(StrEnum):
    # Text.
    # 文本。
    text = "text"
    # Multimodal content, that is, a combination of text and files, or a combination of text and images.
    # 多模态内容，即文本和文件的组合、文本和图片的组合。
    object_string = "object_string"
    # message card. This enum value only appears in the interface response and is not supported as an input parameter.
    # 卡片。此枚举值仅在接口响应中出现，不支持作为入参。
    card = "card"


class MessageObjectStringType(StrEnum):
    """
    The content type of the multimodal message.
    """

    text = "text"
    file = "file"
    image = "image"


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
    # type: # MessageType
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

    @staticmethod
    def user_text_message(content: str, meta_data: Optional[Dict[str, str]] = None) -> "Message":
        return Message(
            role=MessageRole.user,
            type=MessageType.question,
            content=content,
            content_type=MessageContentType.text,
            meta_data=meta_data,
        )

    @staticmethod
    def assistant_text_message(content: str, meta_data: Optional[Dict[str, str]] = None) -> "Message":
        return Message(
            role=MessageRole.assistant,
            type=MessageType.answer,
            content=content,
            content_type=MessageContentType.text,
            meta_data=meta_data,
        )


class Conversation(CozeModel):
    id: str
    created_at: int
    meta_data: Dict[str, str]


class ConversationClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester

    def create_v1(self, *, messages: List[Message] = None, meta_data: Dict[str, str] = None) -> Conversation:
        """
        Create a conversation.
        Conversation is an interaction between a bot and a user, including one or more messages.
        """
        url = f"{self._base_url}/v1/conversation/create"
        body = {
            "messages": [i.model_dump() for i in messages] if len(messages) > 0 else [],
            "meta_data": meta_data,
        }
        return self._requester.request("get", url, Conversation, body=body)
