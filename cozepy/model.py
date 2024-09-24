from enum import Enum
from typing import TypeVar, Generic, List, Optional, Dict

from pydantic import BaseModel, ConfigDict

T = TypeVar("T", bound=BaseModel)


class CozeModel(BaseModel):
    model_config = ConfigDict(protected_namespaces=())


class PagedBase(Generic[T]):
    """
    list api result base.
    """

    def __init__(self, items: List[T], has_more: bool):
        self.items = items
        self.has_more = has_more

    def __repr__(self):
        return f"PagedBase(items={self.items}, has_more={self.has_more})"


class TokenPaged(PagedBase[T]):
    """
    list api, which params is page_token + page_size,
    return is next_page_token + has_more.
    """

    def __init__(self, items: List[T], next_page_token: str = "", has_more: bool = None):
        has_more = has_more if has_more is not None else next_page_token != ""
        super().__init__(items, has_more)
        self.next_page_token = next_page_token

    def __repr__(self):
        return f"TokenPaged(items={self.items}, next_page_token={self.next_page_token})"


class NumberPaged(PagedBase[T]):
    def __init__(self, items: List[T], page_num: int, page_size: int, total: int = None):
        has_more = len(items) >= page_size
        super().__init__(items, has_more)
        self.page_num = page_num
        self.page_size = page_size
        self.total = total

    def __repr__(self):
        return (
            f"NumberPaged(items={self.items}, page_num={self.page_num}, page_size={self.page_size}, total={self.total})"
        )


class MessageRole(str, Enum):
    # Indicates that the content of the message is sent by the user.
    user = "user"
    # Indicates that the content of the message is sent by the bot.
    assistant = "assistant"


class MessageType(str, Enum):
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


class MessageContentType(str, Enum):
    # Text.
    # 文本。
    text = "text"
    # Multimodal content, that is, a combination of text and files, or a combination of text and images.
    # 多模态内容，即文本和文件的组合、文本和图片的组合。
    object_string = "object_string"
    # message card. This enum value only appears in the interface response and is not supported as an input parameter.
    # 卡片。此枚举值仅在接口响应中出现，不支持作为入参。
    card = "card"


class MessageObjectStringType(str, Enum):
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
    type: MessageType
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

    id: str = None
    conversation_id: str = None
    bot_id: str = None
    chat_id: str = None
    created_at: int = None
    updated_at: int = None

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


class ChatStatus(str, Enum):
    """
    The running status of the session
    """

    # The session has been created.
    created = "created"

    # The Bot is processing.
    in_progress = "in_progress"

    # The Bot has finished processing, and the session has ended.
    completed = "completed"

    # The session has failed.
    failed = "failed"

    # The session is interrupted and requires further processing.
    requires_action = "requires_action"


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

    # The running status of the session. The values are:
    # created: The session has been created.
    # in_progress: The Bot is processing.
    # completed: The Bot has finished processing, and the session has ended.
    # failed: The session has failed.
    # requires_action: The session is interrupted and requires further processing.
    status: ChatStatus

    # Details of the information needed for execution.
