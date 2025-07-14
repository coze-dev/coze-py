from typing import Any, Callable, Dict, List, Optional, Union

from pydantic import BaseModel

from cozepy import Chat, Message, ToolOutput
from cozepy.model import DynamicStrEnum
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash
from cozepy.websockets.audio.transcriptions import (
    InputAudioBufferAppendEvent,
    InputAudioBufferClearedEvent,
    InputAudioBufferClearEvent,
    InputAudioBufferCompletedEvent,
    InputAudioBufferCompleteEvent,
)
from cozepy.websockets.ws import (
    AsyncWebsocketsBaseClient,
    AsyncWebsocketsBaseEventHandler,
    InputAudio,
    OutputAudio,
    WebsocketsBaseClient,
    WebsocketsBaseEventHandler,
    WebsocketsEvent,
    WebsocketsEventFactory,
    WebsocketsEventType,
)


# req
class ChatUpdateEvent(WebsocketsEvent):
    """更新对话配置

    此事件可以更新当前对话连接的配置项，若更新成功，会收到 chat.updated 的下行事件，否则，会收到 error 下行事件。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#91642fa8
    """

    class ChatConfig(BaseModel):
        # 标识对话发生在哪一次会话中。会话是智能体和用户之间的一段问答交互。一个会话包含一条或多条消息。对话是会话中对智能体的一次调用，智能体会将对话中产生的消息添加到会话中。可以使用已创建的会话，会话中已存在的消息将作为上下文传递给模型。创建会话的方式可参考创建会话。对于一问一答等不需要区分 conversation 的场合可不传该参数，系统会自动生成一个会话。不传的话会默认创建一个新的 conversation。
        conversation_id: Optional[str] = None
        # 标识当前与智能体的用户，由使用方自行定义、生成与维护。user_id 用于标识对话中的不同用户，不同的 user_id，其对话的上下文消息、数据库等对话记忆数据互相隔离。如果不需要用户数据隔离，可将此参数固定为一个任意字符串，例如 123，abc 等。
        user_id: Optional[str] = None
        # 附加信息，通常用于封装一些业务相关的字段。查看对话消息详情时，系统会透传此附加信息。自定义键值对，应指定为 Map 对象格式。长度为 16 对键值对，其中键（key）的长度范围为 1～64 个字符，值（value）的长度范围为 1～512 个字符。
        meta_data: Optional[Dict[str, str]] = None
        # 智能体中定义的变量。在智能体 prompt 中设置变量 {{key}} 后，可以通过该参数传入变量值，同时支持 Jinja2 语法。详细说明可参考变量示例。变量名只支持英文字母和下划线。
        custom_variables: Optional[Dict[str, str]] = None
        # 附加参数，通常用于特殊场景下指定一些必要参数供模型判断，例如指定经纬度，并询问智能体此位置的天气。自定义键值对格式，其中键（key）仅支持设置为：latitude（纬度，此时值（Value）为纬度值，例如 39.9800718）。longitude（经度，此时值（Value）为经度值，例如 116.309314）。
        extra_params: Optional[Dict[str, str]] = None
        # 是否保存本次对话记录。true：（默认）会话中保存本次对话记录，包括本次对话的模型回复结果、模型执行中间结果。false：会话中不保存本次对话记录，后续也无法通过任何方式查看本次对话信息、消息详情。在同一个会话中再次发起对话时，本次会话也不会作为上下文传递给模型。
        auto_save_history: Optional[bool] = None
        # 设置对话流的自定义输入参数的值，具体用法和示例代码可参考[为自定义参数赋值](https://www.coze.cn/open/docs/tutorial/variable)。 对话流的输入参数 USER_INPUT 应在 additional_messages 中传入，在 parameters 中的 USER_INPUT 不生效。 如果 parameters 中未指定 CONVERSATION_NAME 或其他输入参数，则使用参数默认值运行对话流；如果指定了这些参数，则使用指定值。
        parameters: Optional[Dict[str, Any]] = None

    class TurnDetectionType(DynamicStrEnum):
        # server_vad ：自由对话模式，语音数据会传输到服务器端进行实时分析，服务器端的语音活动检测算法会判断用户是否在说话。
        SERVER_VAD = "server_vad"
        # client_interrupt：（默认）按键说话模式，客户端实时分析语音数据，并检测用户是否已停止说话。
        CLIENT_INTERRUPT = "client_interrupt"

    class InterruptConfigMode(DynamicStrEnum):
        # keyword_contains模式下，说话内容包含关键词才会打断模型回复。例如关键词"扣子"，用户正在说“你好呀扣子......” / “扣子你好呀”，模型回复都会被打断。
        KEYWORD_CONTAINS = "keyword_contains"
        # keyword_prefix模式下，说话内容前缀匹配关键词才会打断模型回复。例如关键词"扣子"，用户正在说“扣子你好呀......”，模型回复就会被打断，而用户说“你好呀扣子......”，模型回复不会被打断。
        KEYWORD_PREFIX = "keyword_prefix"

    class ASRConfigUserLanguage(DynamicStrEnum):
        COMMON = "common"  # 大模型语音识别，可自动识别中英粤。
        ZH = "zh"  # 小模型语音识别，中文。
        CANT = "cant"  # 小模型语音识别，粤语。
        SC = "sc"  # 小模型语音识别，川渝。
        EN = "en"  # 小模型语音识别，英语。
        JA = "ja"  # 小模型语音识别，日语。
        KO = "ko"  # 小模型语音识别，韩语。
        FR = "fr"  # 小模型语音识别，法语。
        ID = "id"  # 小模型语音识别，印尼语。
        ES = "es"  # 小模型语音识别，西班牙语。
        PT = "pt"  # 小模型语音识别，葡萄牙语。
        MS = "ms"  # 小模型语音识别，马来语。
        RU = "ru"  # 小模型语音识别，俄语。

    class ASRConfig(BaseModel):
        # 请输入热词列表，以便提升这些词汇的识别准确率。所有热词加起来最多100个 Tokens，超出部分将自动截断。
        hot_words: Optional[List[str]] = None
        # 请输入上下文信息。最多输入 800 个 Tokens，超出部分将自动截断。
        context: Optional[str] = None
        # 请输入上下文信息。最多输入 800 个 Tokens，超出部分将自动截断。
        context_type: Optional[str] = None
        # 用户说话的语种，默认为 common。选项包括：
        user_language: Optional["ChatUpdateEvent.ASRConfigUserLanguage"] = None
        # 将语音转为文本时，是否启用语义顺滑。默认为 true。true：系统在进行语音处理时，会去掉识别结果中诸如 “啊”“嗯” 等语气词，使得输出的文本语义更加流畅自然，符合正常的语言表达习惯，尤其适用于对文本质量要求较高的场景，如正式的会议记录、新闻稿件生成等。false：系统不会对识别结果中的语气词进行处理，识别结果会保留原始的语气词。
        enable_ddc: Optional[bool] = None
        # 将语音转为文本时，是否开启文本规范化（ITN）处理，将识别结果转换为更符合书面表达习惯的格式以提升可读性。默认为 true。开启后，会将口语化数字转换为标准数字格式，示例：将两点十五分转换为 14:15。将一百美元转换为 $100。
        enable_itn: Optional[bool] = None
        # 将语音转为文本时，是否给文本加上标点符号。默认为 true。
        enable_punc: Optional[bool] = None

    class InterruptConfig(BaseModel):
        # 打断模式
        mode: Optional["ChatUpdateEvent.InterruptConfigMode"] = None
        # 打断的关键词配置，最多同时限制 5 个关键词，每个关键词限定长度在6-24个字节以内(2-8个汉字以内), 不能有标点符号。
        keywords: Optional[List[str]] = None

    class TurnDetection(BaseModel):
        # 用户演讲检测模式
        type: Optional["ChatUpdateEvent.TurnDetectionType"] = None
        # server_vad 模式下，VAD 检测到语音之前要包含的音频量，单位为 ms。默认为 600ms。
        prefix_padding_ms: Optional[int] = None
        # server_vad 模式下，检测语音停止的静音持续时间，单位为 ms。默认为 500ms。
        silence_duration_ms: Optional[int] = None
        # server_vad 模式下打断策略配置
        interrupt_config: Optional["ChatUpdateEvent.InterruptConfig"] = None

    class Data(BaseModel):
        # 输出音频格式。
        output_audio: Optional[OutputAudio] = None
        # 输入音频格式。
        input_audio: Optional[InputAudio] = None
        # 对话配置。
        chat_config: Optional["ChatUpdateEvent.ChatConfig"] = None
        # 需要订阅下行事件的事件类型列表。不设置或者设置为空为订阅所有下行事件。
        event_subscriptions: Optional[List[str]] = None
        # 是否需要播放开场白，默认为 false。
        need_play_prologue: Optional[bool] = None
        # 自定义开场白，need_play_prologue 设置为 true 时生效。如果不设定自定义开场白则使用智能体上设置的开场白。
        prologue_content: Optional[str] = None
        # 转检测配置。
        turn_detection: Optional["ChatUpdateEvent.TurnDetection"] = None
        # 语音识别配置，包括热词和上下文信息，以便优化语音识别的准确性和相关性。
        asr_config: Optional["ChatUpdateEvent.ASRConfig"] = None

    event_type: WebsocketsEventType = WebsocketsEventType.CHAT_UPDATE
    data: Data


# req
class ConversationMessageCreateEvent(WebsocketsEvent):
    """手动提交对话内容

    若 role=user，提交事件后就会生成语音回复，适合如下的场景，比如帮我解析 xx 链接，帮我分析这个图片的内容等。若 role=assistant，提交事件后会加入到对话的上下文。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#46f6a7d0
    """

    class Data(BaseModel):
        # 发送这条消息的实体。取值：user（代表该条消息内容是用户发送的）、assistant（代表该条消息内容是智能体发送的）。
        role: str
        # 消息内容的类型，支持设置为：text：文本。object_string：多模态内容，即文本和文件的组合、文本和图片的组合。
        content_type: str
        # 消息的内容，支持纯文本、多模态（文本、图片、文件混合输入）、卡片等多种类型的内容。当 content_type 为 object_string时，content 的结构和详细参数说明请参见object_string object。
        content: str

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_MESSAGE_CREATE
    data: Data


# req
class ConversationClear(WebsocketsEvent):
    """清除上下文

    清除上下文，会在当前 conversation 下新增一个 section，服务端处理完后会返回 conversation.cleared 事件。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#aa86f213
    """

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CLEAR


# req
class ConversationChatSubmitToolOutputsEvent(WebsocketsEvent):
    """提交端插件执行结果

    你可以将需要客户端执行的操作定义为插件，对话中如果触发这个插件，会收到一个 event_type = "conversation.chat.requires_action" 的下行事件，此时需要执行客户端的操作后，通过此上行事件来提交插件执行后的结果。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#aacdcb41
    """

    class Data(BaseModel):
        # 对话的唯一标识。
        chat_id: str
        # 工具执行结果。
        tool_outputs: List[ToolOutput]

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CHAT_SUBMIT_TOOL_OUTPUTS
    data: Data


# req
class ConversationChatCancelEvent(WebsocketsEvent):
    """打断智能体输出

    发送此事件可取消正在进行的对话，中断后，服务端将会返回 conversation.chat.canceled 事件。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#0554db7d
    """

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CHAT_CANCEL


# req
class InputTextGenerateAudioEvent(WebsocketsEvent):
    """提交文字用于语音合成

    你可以主动提交一段文字用来做语音合成，提交的消息不会触发智能体的回复，只会合成音频内容下发到客户端。
    提交事件的时候如果智能体正在输出语音会被中断输出。适合在和智能体聊天过程中客户端长时间没有响应，
    智能体可以主动说话暖场的场景。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#620367d0
    """

    class Mode(DynamicStrEnum):
        TEXT = "text"

    class Data(BaseModel):
        # 消息内容的类型，支持设置为：text：文本
        mode: "InputTextGenerateAudioEvent.Mode"
        # 当 mode == text 时候必填。长度限制 (0, 1024) 字节
        text: Optional[str] = None

    event_type: WebsocketsEventType = WebsocketsEventType.INPUT_TEXT_GENERATE_AUDIO
    data: Data


# resp
class ChatCreatedEvent(WebsocketsEvent):
    """对话连接成功

    流式对话接口成功建立连接后服务端会发送此事件。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#a061f115
    """

    event_type: WebsocketsEventType = WebsocketsEventType.CHAT_CREATED


# resp
class ChatUpdatedEvent(WebsocketsEvent):
    """对话配置成功

    对话配置更新成功后，会返回最新的配置。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#39879618
    """

    event_type: WebsocketsEventType = WebsocketsEventType.CHAT_UPDATED
    data: ChatUpdateEvent.Data


# resp
class ConversationChatCreatedEvent(WebsocketsEvent):
    """对话开始

    创建对话的事件，表示对话开始。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#a2b10fd2
    """

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CHAT_CREATED
    data: Chat


# resp
class ConversationChatInProgressEvent(WebsocketsEvent):
    """对话正在处理

    服务端正在处理对话。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#36a38a6b
    """

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CHAT_IN_PROGRESS
    data: Chat


# resp
class ConversationMessageDeltaEvent(WebsocketsEvent):
    """增量消息

    增量消息，通常是 type=answer 时的增量消息。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#2dfe8dba
    """

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_MESSAGE_DELTA
    data: Message


# resp
class ConversationAudioSentenceStartEvent(WebsocketsEvent):
    """增量语音字幕

    一条新的字幕句子，后续的 conversation.audio.delta 增量语音均属于当前字幕句子，可能有多个增量语音共同对应此句字幕的文字内容。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#2e67bf44
    """

    class Data(BaseModel):
        # 新字幕句子的文本内容，后续相关 conversation.audio.delta 增量语音均对应此文本。
        text: str

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_AUDIO_SENTENCE_START
    data: Data


# resp
class ConversationMessageCompletedEvent(WebsocketsEvent):
    """消息完成

    消息已回复完成。此时事件中带有所有 message.delta 的拼接结果，且每个消息均为 completed 状态。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#4361e8d1
    """

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_MESSAGE_COMPLETED
    data: Message


# resp
class ConversationAudioCompletedEvent(WebsocketsEvent):
    """语音回复完成

    语音回复完成，表示对话结束。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#b00d6a73
    """

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_AUDIO_COMPLETED
    data: Message


# resp
class ConversationAudioTranscriptCompletedEvent(WebsocketsEvent):
    """用户语音识别完成

    用户语音识别完成，表示用户语音识别完成。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#9d1e6930
    """

    class Data(BaseModel):
        # 语音识别的最终结果。
        content: str

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_AUDIO_TRANSCRIPT_COMPLETED
    data: Data


# resp
class ConversationChatRequiresActionEvent(WebsocketsEvent):
    """端插件请求

    对话中断，需要使用方上报工具的执行结果。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#2ef697d8
    """

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CHAT_REQUIRES_ACTION
    data: Chat


# resp
class InputAudioBufferSpeechStartedEvent(WebsocketsEvent):
    """用户开始说话

    此事件表示服务端识别到用户正在说话。只有在 server_vad 模式下，才会返回此事件。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#95553c68
    """

    event_type: WebsocketsEventType = WebsocketsEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED


# resp
class InputAudioBufferSpeechStoppedEvent(WebsocketsEvent):
    """用户结束说话

    此事件表示服务端识别到用户已停止说话。只有在 server_vad 模式下，才会返回此事件。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#5084c0aa
    """

    event_type: WebsocketsEventType = WebsocketsEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED


# resp
class ConversationAudioDeltaEvent(WebsocketsEvent):
    """增量语音

    增量消息，通常是 type=answer 时的增量消息。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#36a38a6b
    """

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_AUDIO_DELTA
    data: Message


# resp
class ConversationChatCompletedEvent(WebsocketsEvent):
    """对话完成

    对话完成，表示对话结束。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#02fac327
    """

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CHAT_COMPLETED
    data: Chat


# resp
class ConversationChatFailedEvent(WebsocketsEvent):
    """对话失败

    此事件用于标识对话失败。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#765bb7e5
    """

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CHAT_FAILED
    data: Chat


# resp
class ConversationClearedEvent(WebsocketsEvent):
    """上下文清除完成

    上下文清除完成，表示上下文已清除。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#6a941b8a
    """

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CLEARED


# resp
class ConversationChatCanceledEvent(WebsocketsEvent):
    """智能体输出中断

    客户端提交 conversation.chat.cancel 事件，服务端完成中断后，将返回此事件。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#089ed144
    """

    class Data(BaseModel):
        # 输出中断类型枚举值，包括 1: 被用户语音说话打断  2: 用户主动 cancel  3: 手动提交对话内容
        code: int
        # 智能体输出中断的详细说明
        msg: str

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CHAT_CANCELED
    data: Data


# resp
class ConversationAudioTranscriptUpdateEvent(WebsocketsEvent):
    """用户语音识别字幕

    用户语音识别的中间值，每次返回都是全量文本。
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#1b59cbf9
    """

    class Data(BaseModel):
        # 语音识别的中间值。
        content: str

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_AUDIO_TRANSCRIPT_UPDATE
    data: Data


_chat_event_factory = WebsocketsEventFactory(
    {
        WebsocketsEventType.CHAT_CREATED.value: ChatCreatedEvent,
        WebsocketsEventType.CHAT_UPDATED.value: ChatUpdatedEvent,
        WebsocketsEventType.CONVERSATION_CHAT_CREATED.value: ConversationChatCreatedEvent,
        WebsocketsEventType.CONVERSATION_CHAT_IN_PROGRESS.value: ConversationChatInProgressEvent,
        WebsocketsEventType.CONVERSATION_MESSAGE_DELTA.value: ConversationMessageDeltaEvent,
        WebsocketsEventType.CONVERSATION_AUDIO_SENTENCE_START.value: ConversationAudioSentenceStartEvent,
        WebsocketsEventType.CONVERSATION_AUDIO_DELTA.value: ConversationAudioDeltaEvent,
        WebsocketsEventType.CONVERSATION_MESSAGE_COMPLETED.value: ConversationMessageCompletedEvent,
        WebsocketsEventType.CONVERSATION_AUDIO_COMPLETED.value: ConversationAudioCompletedEvent,
        WebsocketsEventType.CONVERSATION_CHAT_COMPLETED.value: ConversationChatCompletedEvent,
        WebsocketsEventType.CONVERSATION_CHAT_FAILED.value: ConversationChatFailedEvent,
        WebsocketsEventType.INPUT_AUDIO_BUFFER_COMPLETED.value: InputAudioBufferCompletedEvent,
        WebsocketsEventType.INPUT_AUDIO_BUFFER_CLEARED.value: InputAudioBufferClearedEvent,
        WebsocketsEventType.CONVERSATION_CLEARED.value: ConversationClearedEvent,
        WebsocketsEventType.CONVERSATION_CHAT_CANCELED.value: ConversationChatCanceledEvent,
        WebsocketsEventType.CONVERSATION_AUDIO_TRANSCRIPT_UPDATE.value: ConversationAudioTranscriptUpdateEvent,
        WebsocketsEventType.CONVERSATION_AUDIO_TRANSCRIPT_COMPLETED.value: ConversationAudioTranscriptCompletedEvent,
        WebsocketsEventType.CONVERSATION_CHAT_REQUIRES_ACTION.value: ConversationChatRequiresActionEvent,
        WebsocketsEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED.value: InputAudioBufferSpeechStartedEvent,
        WebsocketsEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED.value: InputAudioBufferSpeechStoppedEvent,
    }
)


class WebsocketsChatEventHandler(WebsocketsBaseEventHandler):
    # 对话连接成功
    def on_chat_created(self, cli: "WebsocketsChatClient", event: ChatCreatedEvent):
        pass

    # 对话配置成功
    def on_chat_updated(self, cli: "WebsocketsChatClient", event: ChatUpdatedEvent):
        pass

    # 对话开始
    def on_conversation_chat_created(self, cli: "WebsocketsChatClient", event: ConversationChatCreatedEvent):
        pass

    # 对话正在处理
    def on_conversation_chat_in_progress(self, cli: "WebsocketsChatClient", event: ConversationChatInProgressEvent):
        pass

    # 增量消息
    def on_conversation_message_delta(self, cli: "WebsocketsChatClient", event: ConversationMessageDeltaEvent):
        pass

    # 增量语音字幕
    def on_conversation_audio_sentence_start(
        self, cli: "WebsocketsChatClient", event: ConversationAudioSentenceStartEvent
    ):
        pass

    # 增量语音
    def on_conversation_audio_delta(self, cli: "WebsocketsChatClient", event: ConversationAudioDeltaEvent):
        pass

    # 消息完成
    def on_conversation_message_completed(self, cli: "WebsocketsChatClient", event: ConversationMessageCompletedEvent):
        pass

    # 语音回复完成
    def on_conversation_audio_completed(self, cli: "WebsocketsChatClient", event: ConversationAudioCompletedEvent):
        pass

    # 对话完成
    def on_conversation_chat_completed(self, cli: "WebsocketsChatClient", event: ConversationChatCompletedEvent):
        pass

    # 对话失败
    def on_conversation_chat_failed(self, cli: "WebsocketsChatClient", event: ConversationChatFailedEvent):
        pass

    # 音频提交完成
    def on_input_audio_buffer_completed(self, cli: "WebsocketsChatClient", event: InputAudioBufferCompletedEvent):
        pass

    # 音频清除成功
    def on_input_audio_buffer_cleared(self, cli: "WebsocketsChatClient", event: InputAudioBufferClearedEvent):
        pass

    # 上下文清除完成
    def on_conversation_cleared(self, cli: "WebsocketsChatClient", event: ConversationClearedEvent):
        pass

    # 智能体输出中断
    def on_conversation_chat_canceled(self, cli: "WebsocketsChatClient", event: ConversationChatCanceledEvent):
        pass

    # 用户语音识别字幕
    def on_conversation_audio_transcript_update(
        self, cli: "WebsocketsChatClient", event: ConversationAudioTranscriptUpdateEvent
    ):
        pass

    # 用户语音识别完成
    def on_conversation_audio_transcript_completed(
        self, cli: "WebsocketsChatClient", event: ConversationAudioTranscriptCompletedEvent
    ):
        pass

    # 端插件请求
    def on_conversation_chat_requires_action(
        self, cli: "WebsocketsChatClient", event: ConversationChatRequiresActionEvent
    ):
        pass

    # 用户开始说话
    def on_input_audio_buffer_speech_started(
        self, cli: "WebsocketsChatClient", event: InputAudioBufferSpeechStartedEvent
    ):
        pass

    # 用户结束说话
    def on_input_audio_buffer_speech_stopped(
        self, cli: "WebsocketsChatClient", event: InputAudioBufferSpeechStoppedEvent
    ):
        pass


class WebsocketsChatClient(WebsocketsBaseClient):
    def __init__(
        self,
        base_url: str,
        requester: Requester,
        bot_id: str,
        on_event: Union[WebsocketsChatEventHandler, Dict[WebsocketsEventType, Callable]],
        workflow_id: Optional[str] = None,
        device_id: Optional[int] = None,
        **kwargs,
    ):
        if isinstance(on_event, WebsocketsChatEventHandler):
            on_event = on_event.to_dict()
        super().__init__(
            base_url=base_url,
            requester=requester,
            path="v1/chat",
            event_factory=_chat_event_factory,
            query=remove_none_values(
                {
                    "bot_id": bot_id,
                    "workflow_id": workflow_id,
                    "device_id": str(device_id) if device_id is not None else None,
                }
            ),
            on_event=on_event,  # type: ignore
            wait_events=[WebsocketsEventType.CONVERSATION_CHAT_COMPLETED],
            **kwargs,
        )

    # 更新对话配置
    def chat_update(self, data: ChatUpdateEvent.Data) -> None:
        self._input_queue.put(ChatUpdateEvent.model_validate({"data": data}))

    # 流式上传音频片段
    def input_audio_buffer_append(self, data: InputAudioBufferAppendEvent.Data) -> None:
        self._input_queue.put(InputAudioBufferAppendEvent.model_validate({"data": data}))

    # 提交音频
    def input_audio_buffer_complete(self) -> None:
        self._input_queue.put(InputAudioBufferCompleteEvent.model_validate({}))

    # 清除缓冲区音频
    def input_audio_buffer_clear(self) -> None:
        self._input_queue.put(InputAudioBufferClearEvent.model_validate({}))

    # 手动提交对话内容
    def conversation_chat_submit_tool_outputs(self, data: ConversationChatSubmitToolOutputsEvent.Data) -> None:
        self._input_queue.put(ConversationChatSubmitToolOutputsEvent.model_validate({"data": data}))

    # 清除上下文
    def conversation_clear(self) -> None:
        self._input_queue.put(ConversationClear.model_validate({}))

    # 提交端插件执行结果
    def conversation_chat_cancel(self) -> None:
        self._input_queue.put(ConversationChatCancelEvent.model_validate({}))

    # 打断智能体输出
    def conversation_message_create(self, data: ConversationMessageCreateEvent.Data) -> None:
        self._input_queue.put(ConversationMessageCreateEvent.model_validate({"data": data}))

    # 提交文字用于语音合成
    def input_text_generate_audio(self, data: InputTextGenerateAudioEvent.Data) -> None:
        self._input_queue.put(InputTextGenerateAudioEvent.model_validate({"data": data}))


class WebsocketsChatBuildClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(
        self,
        *,
        bot_id: str,
        on_event: Union[WebsocketsChatEventHandler, Dict[WebsocketsEventType, Callable]],
        workflow_id: Optional[str] = None,
        device_id: Optional[int] = None,
        **kwargs,
    ) -> WebsocketsChatClient:
        return WebsocketsChatClient(
            base_url=self._base_url,
            requester=self._requester,
            bot_id=bot_id,
            on_event=on_event,  # type: ignore
            workflow_id=workflow_id,
            device_id=device_id,
            **kwargs,
        )


class AsyncWebsocketsChatEventHandler(AsyncWebsocketsBaseEventHandler):
    # 对话连接成功
    async def on_chat_created(self, cli: "AsyncWebsocketsChatClient", event: ChatCreatedEvent):
        pass

    # 对话配置成功
    async def on_chat_updated(self, cli: "AsyncWebsocketsChatClient", event: ChatUpdatedEvent):
        pass

    # 对话开始
    async def on_conversation_chat_created(self, cli: "AsyncWebsocketsChatClient", event: ConversationChatCreatedEvent):
        pass

    # 对话正在处理
    async def on_conversation_chat_in_progress(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationChatInProgressEvent
    ):
        pass

    # 增量消息
    async def on_conversation_message_delta(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationMessageDeltaEvent
    ):
        pass

    # 增量语音字幕
    async def on_conversation_audio_sentence_start(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationAudioSentenceStartEvent
    ):
        pass

    # 增量语音
    async def on_conversation_audio_delta(self, cli: "AsyncWebsocketsChatClient", event: ConversationAudioDeltaEvent):
        pass

    # 消息完成
    async def on_conversation_message_completed(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationMessageCompletedEvent
    ):
        pass

    # 语音回复完成
    async def on_conversation_audio_completed(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationAudioCompletedEvent
    ):
        pass

    # 对话完成
    async def on_conversation_chat_completed(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationChatCompletedEvent
    ):
        pass

    # 对话失败
    async def on_conversation_chat_failed(self, cli: "AsyncWebsocketsChatClient", event: ConversationChatFailedEvent):
        pass

    # 音频提交完成
    async def on_input_audio_buffer_completed(
        self, cli: "AsyncWebsocketsChatClient", event: InputAudioBufferCompletedEvent
    ):
        pass

    # 音频清除成功
    async def on_input_audio_buffer_cleared(
        self, cli: "AsyncWebsocketsChatClient", event: InputAudioBufferClearedEvent
    ):
        pass

    # 上下文清除完成
    async def on_conversation_cleared(self, cli: "AsyncWebsocketsChatClient", event: ConversationClearedEvent):
        pass

    # 智能体输出中断
    async def on_conversation_chat_canceled(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationChatCanceledEvent
    ):
        pass

    # 用户语音识别字幕
    async def on_conversation_audio_transcript_update(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationAudioTranscriptUpdateEvent
    ):
        pass

    # 用户语音识别完成
    async def on_conversation_audio_transcript_completed(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationAudioTranscriptCompletedEvent
    ):
        pass

    # 端插件请求
    async def on_conversation_chat_requires_action(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationChatRequiresActionEvent
    ):
        pass

    # 用户开始说话
    async def on_input_audio_buffer_speech_started(
        self, cli: "AsyncWebsocketsChatClient", event: InputAudioBufferSpeechStartedEvent
    ):
        pass

    # 用户结束说话
    async def on_input_audio_buffer_speech_stopped(
        self, cli: "AsyncWebsocketsChatClient", event: InputAudioBufferSpeechStoppedEvent
    ):
        pass


class AsyncWebsocketsChatClient(AsyncWebsocketsBaseClient):
    def __init__(
        self,
        base_url: str,
        requester: Requester,
        bot_id: str,
        on_event: Union[AsyncWebsocketsChatEventHandler, Dict[WebsocketsEventType, Callable]],
        workflow_id: Optional[str] = None,
        device_id: Optional[int] = None,
        **kwargs,
    ):
        if isinstance(on_event, AsyncWebsocketsChatEventHandler):
            on_event = on_event.to_dict()
        super().__init__(
            base_url=base_url,
            requester=requester,
            path="v1/chat",
            event_factory=_chat_event_factory,
            query=remove_none_values(
                {
                    "bot_id": bot_id,
                    "workflow_id": workflow_id,
                    "device_id": str(device_id) if device_id is not None else None,
                }
            ),
            on_event=on_event,  # type: ignore
            wait_events=[WebsocketsEventType.CONVERSATION_CHAT_COMPLETED],
            **kwargs,
        )

    # 更新对话配置
    async def chat_update(self, data: ChatUpdateEvent.Data) -> None:
        await self._input_queue.put(ChatUpdateEvent.model_validate({"data": data}))

    # 流式上传音频片段
    async def input_audio_buffer_append(self, data: InputAudioBufferAppendEvent.Data) -> None:
        await self._input_queue.put(InputAudioBufferAppendEvent.model_validate({"data": data}))

    # 提交音频
    async def input_audio_buffer_complete(self) -> None:
        await self._input_queue.put(InputAudioBufferCompleteEvent.model_validate({}))

    # 清除缓冲区音频
    async def input_audio_buffer_clear(self) -> None:
        await self._input_queue.put(InputAudioBufferClearEvent.model_validate({}))

    # 手动提交对话内容
    async def conversation_chat_submit_tool_outputs(self, data: ConversationChatSubmitToolOutputsEvent.Data) -> None:
        await self._input_queue.put(ConversationChatSubmitToolOutputsEvent.model_validate({"data": data}))

    # 清除上下文
    async def conversation_clear(self) -> None:
        await self._input_queue.put(ConversationClear.model_validate({}))

    # 提交端插件执行结果
    async def conversation_chat_cancel(self) -> None:
        await self._input_queue.put(ConversationChatCancelEvent.model_validate({}))

    # 打断智能体输出
    async def conversation_message_create(self, data: ConversationMessageCreateEvent.Data) -> None:
        await self._input_queue.put(ConversationMessageCreateEvent.model_validate({"data": data}))

    # 提交文字用于语音合成
    async def input_text_generate_audio(self, data: InputTextGenerateAudioEvent.Data) -> None:
        await self._input_queue.put(InputTextGenerateAudioEvent.model_validate({"data": data}))


class AsyncWebsocketsChatBuildClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(
        self,
        *,
        bot_id: str,
        on_event: Union[AsyncWebsocketsChatEventHandler, Dict[WebsocketsEventType, Callable]],
        workflow_id: Optional[str] = None,
        device_id: Optional[int] = None,
        **kwargs,
    ) -> AsyncWebsocketsChatClient:
        return AsyncWebsocketsChatClient(
            base_url=self._base_url,
            requester=self._requester,
            bot_id=bot_id,
            on_event=on_event,  # type: ignore
            workflow_id=workflow_id,
            device_id=device_id,
            **kwargs,
        )
