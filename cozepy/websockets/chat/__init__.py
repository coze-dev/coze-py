from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from pydantic import BaseModel

from cozepy import Chat, Message, ToolOutput
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash
from cozepy.websockets.audio.transcriptions import (
    InputAudioBufferAppendEvent,
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
    WebsocketsEventType,
)


# common
class TurnDetection(BaseModel):
    class TurnDetectionType(str, Enum):
        # server_vad ：自由对话模式，语音数据会传输到服务器端进行实时分析，服务器端的语音活动检测算法会判断用户是否在说话。
        SERVER_VAD = "server_vad"
        # client_interrupt：（默认）按键说话模式，客户端实时分析语音数据，并检测用户是否已停止说话。
        CLIENT_INTERRUPT = "client_interrupt"

    class InterruptConfigMode(str, Enum):
        # keyword_contains模式下，说话内容包含关键词才会打断模型回复。例如关键词"扣子"，用户正在说"你好呀扣子......" / "扣子你好呀"，模型回复都会被打断。
        KEYWORD_CONTAINS = "keyword_contains"
        # keyword_prefix模式下，说话内容前缀匹配关键词才会打断模型回复。例如关键词"扣子"，用户正在说"扣子你好呀......"，模型回复就会被打断，而用户说"你好呀扣子......"，模型回复不会被打断。
        KEYWORD_PREFIX = "keyword_prefix"

    class InterruptConfig(BaseModel):
        # 打断模式
        mode: Optional["TurnDetection.InterruptConfigMode"] = None
        # 打断的关键词配置，最多同时限制 5 个关键词，每个关键词限定长度在6-24个字节以内(2-8个汉字以内), 不能有标点符号。
        keywords: Optional[List[str]] = None

    # 用户演讲检测模式
    type: Optional[TurnDetectionType] = None
    # server_vad 模式下，VAD 检测到语音之前要包含的音频量，单位为 ms。默认为 600ms。
    prefix_padding_ms: Optional[int] = None
    # server_vad 模式下，检测语音停止的静音持续时间，单位为 ms。默认为 500ms。
    silence_duration_ms: Optional[int] = None
    # server_vad 模式下打断策略配置
    interrupt_config: Optional[InterruptConfig] = None


class ASRConfig(BaseModel):
    class UserLanguage(str, Enum):
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

    # 请输入热词列表，以便提升这些词汇的识别准确率。所有热词加起来最多100个 Tokens，超出部分将自动截断。
    hot_words: Optional[List[str]] = None
    # 请输入上下文信息。最多输入 800 个 Tokens，超出部分将自动截断。
    context: Optional[str] = None
    # 请输入上下文信息。最多输入 800 个 Tokens，超出部分将自动截断。
    context_type: Optional[str] = None
    # 用户说话的语种，默认为 common。选项包括：
    user_language: Optional[UserLanguage] = None
    # 将语音转为文本时，是否启用语义顺滑。默认为 true。true：系统在进行语音处理时，会去掉识别结果中诸如 "啊""嗯" 等语气词，使得输出的文本语义更加流畅自然，符合正常的语言表达习惯，尤其适用于对文本质量要求较高的场景，如正式的会议记录、新闻稿件生成等。false：系统不会对识别结果中的语气词进行处理，识别结果会保留原始的语气词。
    enable_ddc: Optional[bool] = None
    # 将语音转为文本时，是否开启文本规范化（ITN）处理，将识别结果转换为更符合书面表达习惯的格式以提升可读性。默认为 true。开启后，会将口语化数字转换为标准数字格式，示例：将两点十五分转换为 14:15。将一百美元转换为 $100。
    enable_itn: Optional[bool] = None
    # 将语音转为文本时，是否给文本加上标点符号。默认为 true。
    enable_punc: Optional[bool] = None


# req
class ChatUpdateEvent(WebsocketsEvent):
    """
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
        turn_detection: Optional[TurnDetection] = None
        # 语音识别配置，包括热词和上下文信息，以便优化语音识别的准确性和相关性。
        asr_config: Optional[ASRConfig] = None

    event_type: WebsocketsEventType = WebsocketsEventType.CHAT_UPDATE
    data: Data


# req
class ConversationChatSubmitToolOutputsEvent(WebsocketsEvent):
    class Data(BaseModel):
        chat_id: str
        tool_outputs: List[ToolOutput]

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CHAT_SUBMIT_TOOL_OUTPUTS
    data: Data


# req
class ConversationChatCancelEvent(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CHAT_CANCEL


# req
class ConversationMessageCreateEvent(WebsocketsEvent):
    class Data(BaseModel):
        role: str
        content_type: str
        content: str

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_MESSAGE_CREATE
    data: Data


# resp
class ChatCreatedEvent(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.CHAT_CREATED


# resp
class ChatUpdatedEvent(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.CHAT_UPDATED
    data: ChatUpdateEvent.Data


# resp
class ConversationChatCreatedEvent(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CHAT_CREATED
    data: Chat


# resp
class ConversationChatInProgressEvent(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CHAT_IN_PROGRESS


# resp
class ConversationMessageDeltaEvent(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_MESSAGE_DELTA
    data: Message


# resp
class ConversationAudioTranscriptCompletedEvent(WebsocketsEvent):
    class Data(BaseModel):
        content: str

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_AUDIO_TRANSCRIPT_COMPLETED
    data: Data


# resp
class ConversationMessageCompletedEvent(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_MESSAGE_COMPLETED
    data: Message


# resp
class ConversationChatRequiresActionEvent(WebsocketsEvent):
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
    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_AUDIO_DELTA
    data: Message


# resp
class ConversationAudioCompletedEvent(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_AUDIO_COMPLETED


# resp
class ConversationChatCompletedEvent(WebsocketsEvent):
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
class ConversationChatCanceledEvent(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CHAT_CANCELED


# resp
class ConversationAudioTranscriptUpdateEvent(WebsocketsEvent):
    """用户语音识别字幕
    docs: https://www.coze.cn/open/docs/developer_guides/streaming_chat_event#1b59cbf9
    """

    class Data(BaseModel):
        # 语音识别的中间值。
        content: str

    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_AUDIO_TRANSCRIPT_UPDATE
    data: Data


_chat_event_type_to_class = {
    WebsocketsEventType.CHAT_CREATED.value: ChatCreatedEvent,
    WebsocketsEventType.CHAT_UPDATED.value: ChatUpdatedEvent,
    WebsocketsEventType.INPUT_AUDIO_BUFFER_COMPLETED.value: InputAudioBufferCompletedEvent,
    WebsocketsEventType.CONVERSATION_CHAT_CREATED.value: ConversationChatCreatedEvent,
    WebsocketsEventType.CONVERSATION_CHAT_IN_PROGRESS.value: ConversationChatInProgressEvent,
    WebsocketsEventType.CONVERSATION_MESSAGE_DELTA.value: ConversationMessageDeltaEvent,
    WebsocketsEventType.CONVERSATION_AUDIO_TRANSCRIPT_UPDATE.value: ConversationAudioTranscriptUpdateEvent,
    WebsocketsEventType.CONVERSATION_AUDIO_TRANSCRIPT_COMPLETED.value: ConversationAudioTranscriptCompletedEvent,
    WebsocketsEventType.CONVERSATION_CHAT_REQUIRES_ACTION.value: ConversationChatRequiresActionEvent,
    WebsocketsEventType.CONVERSATION_MESSAGE_COMPLETED.value: ConversationMessageCompletedEvent,
    WebsocketsEventType.CONVERSATION_AUDIO_DELTA.value: ConversationAudioDeltaEvent,
    WebsocketsEventType.CONVERSATION_AUDIO_COMPLETED.value: ConversationAudioCompletedEvent,
    WebsocketsEventType.CONVERSATION_CHAT_COMPLETED.value: ConversationChatCompletedEvent,
    WebsocketsEventType.CONVERSATION_CHAT_FAILED.value: ConversationChatFailedEvent,
    WebsocketsEventType.CONVERSATION_CHAT_CANCELED.value: ConversationChatCanceledEvent,
    WebsocketsEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED.value: InputAudioBufferSpeechStartedEvent,
    WebsocketsEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED.value: InputAudioBufferSpeechStoppedEvent,
}


class WebsocketsChatEventHandler(WebsocketsBaseEventHandler):
    def on_chat_created(self, cli: "WebsocketsChatClient", event: ChatCreatedEvent):
        pass

    def on_chat_updated(self, cli: "WebsocketsChatClient", event: ChatUpdatedEvent):
        pass

    def on_input_audio_buffer_completed(self, cli: "WebsocketsChatClient", event: InputAudioBufferCompletedEvent):
        pass

    def on_conversation_chat_created(self, cli: "WebsocketsChatClient", event: ConversationChatCreatedEvent):
        pass

    def on_conversation_chat_in_progress(self, cli: "WebsocketsChatClient", event: ConversationChatInProgressEvent):
        pass

    def on_conversation_message_delta(self, cli: "WebsocketsChatClient", event: ConversationMessageDeltaEvent):
        pass

    def on_conversation_audio_transcript_update(
        self, cli: "WebsocketsChatClient", event: ConversationAudioTranscriptUpdateEvent
    ):
        pass

    def on_conversation_audio_transcript_completed(
        self, cli: "WebsocketsChatClient", event: ConversationAudioTranscriptCompletedEvent
    ):
        pass

    def on_conversation_message_completed(self, cli: "WebsocketsChatClient", event: ConversationMessageCompletedEvent):
        pass

    def on_conversation_chat_requires_action(
        self, cli: "WebsocketsChatClient", event: ConversationChatRequiresActionEvent
    ):
        pass

    def on_conversation_audio_delta(self, cli: "WebsocketsChatClient", event: ConversationAudioDeltaEvent):
        pass

    def on_conversation_audio_completed(self, cli: "WebsocketsChatClient", event: ConversationAudioCompletedEvent):
        pass

    def on_conversation_chat_completed(self, cli: "WebsocketsChatClient", event: ConversationChatCompletedEvent):
        pass

    def on_conversation_chat_failed(self, cli: "WebsocketsChatClient", event: ConversationChatFailedEvent):
        pass

    def on_conversation_chat_canceled(self, cli: "WebsocketsChatClient", event: ConversationChatCanceledEvent):
        pass

    def on_input_audio_buffer_speech_started(
        self, cli: "WebsocketsChatClient", event: InputAudioBufferSpeechStartedEvent
    ):
        pass

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
        **kwargs,
    ):
        if isinstance(on_event, WebsocketsChatEventHandler):
            on_event = on_event.to_dict()
        super().__init__(
            base_url=base_url,
            requester=requester,
            path="v1/chat",
            query=remove_none_values(
                {
                    "bot_id": bot_id,
                    "workflow_id": workflow_id,
                }
            ),
            on_event=on_event,  # type: ignore
            wait_events=[WebsocketsEventType.CONVERSATION_CHAT_COMPLETED],
            event_type_to_class=_chat_event_type_to_class,
            **kwargs,
        )

    def chat_update(self, data: ChatUpdateEvent.Data) -> None:
        self._input_queue.put(ChatUpdateEvent.model_validate({"data": data}))

    def conversation_chat_submit_tool_outputs(self, data: ConversationChatSubmitToolOutputsEvent.Data) -> None:
        self._input_queue.put(ConversationChatSubmitToolOutputsEvent.model_validate({"data": data}))

    def conversation_chat_cancel(self) -> None:
        self._input_queue.put(ConversationChatCancelEvent.model_validate({}))

    def conversation_message_create(self, data: ConversationMessageCreateEvent.Data) -> None:
        self._input_queue.put(ConversationMessageCreateEvent.model_validate({"data": data}))

    def input_audio_buffer_append(self, data: InputAudioBufferAppendEvent.Data) -> None:
        self._input_queue.put(InputAudioBufferAppendEvent.model_validate({"data": data}))

    def input_audio_buffer_complete(self) -> None:
        self._input_queue.put(InputAudioBufferCompleteEvent.model_validate({}))


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
        **kwargs,
    ) -> WebsocketsChatClient:
        return WebsocketsChatClient(
            base_url=self._base_url,
            requester=self._requester,
            bot_id=bot_id,
            on_event=on_event,  # type: ignore
            workflow_id=workflow_id,
            **kwargs,
        )


class AsyncWebsocketsChatEventHandler(AsyncWebsocketsBaseEventHandler):
    async def on_chat_created(self, cli: "AsyncWebsocketsChatClient", event: ChatCreatedEvent):
        pass

    async def on_chat_updated(self, cli: "AsyncWebsocketsChatClient", event: ChatUpdatedEvent):
        pass

    async def on_input_audio_buffer_completed(
        self, cli: "AsyncWebsocketsChatClient", event: InputAudioBufferCompletedEvent
    ):
        pass

    async def on_conversation_chat_created(self, cli: "AsyncWebsocketsChatClient", event: ConversationChatCreatedEvent):
        pass

    async def on_conversation_chat_in_progress(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationChatInProgressEvent
    ):
        pass

    async def on_conversation_message_delta(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationMessageDeltaEvent
    ):
        pass

    async def on_conversation_audio_transcript_update(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationAudioTranscriptUpdateEvent
    ):
        pass

    async def on_conversation_audio_transcript_completed(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationAudioTranscriptCompletedEvent
    ):
        pass

    async def on_conversation_chat_requires_action(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationChatRequiresActionEvent
    ):
        pass

    async def on_conversation_message_completed(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationMessageCompletedEvent
    ):
        pass

    async def on_conversation_audio_delta(self, cli: "AsyncWebsocketsChatClient", event: ConversationAudioDeltaEvent):
        pass

    async def on_conversation_audio_completed(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationAudioCompletedEvent
    ):
        pass

    async def on_conversation_chat_completed(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationChatCompletedEvent
    ):
        pass

    async def on_conversation_chat_failed(self, cli: "AsyncWebsocketsChatClient", event: ConversationChatFailedEvent):
        pass

    async def on_conversation_chat_canceled(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationChatCanceledEvent
    ):
        pass

    async def on_input_audio_buffer_speech_started(
        self, cli: "AsyncWebsocketsChatClient", event: InputAudioBufferSpeechStartedEvent
    ):
        pass

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
        **kwargs,
    ):
        if isinstance(on_event, AsyncWebsocketsChatEventHandler):
            on_event = on_event.to_dict()
        super().__init__(
            base_url=base_url,
            requester=requester,
            path="v1/chat",
            query=remove_none_values(
                {
                    "bot_id": bot_id,
                    "workflow_id": workflow_id,
                }
            ),
            on_event=on_event,  # type: ignore
            wait_events=[WebsocketsEventType.CONVERSATION_CHAT_COMPLETED],
            event_type_to_class=_chat_event_type_to_class,
            **kwargs,
        )

    async def chat_update(self, data: ChatUpdateEvent.Data) -> None:
        await self._input_queue.put(ChatUpdateEvent.model_validate({"data": data}))

    async def conversation_chat_submit_tool_outputs(self, data: ConversationChatSubmitToolOutputsEvent.Data) -> None:
        await self._input_queue.put(ConversationChatSubmitToolOutputsEvent.model_validate({"data": data}))

    async def conversation_chat_cancel(self) -> None:
        await self._input_queue.put(ConversationChatCancelEvent.model_validate({}))

    async def conversation_message_create(self, data: ConversationMessageCreateEvent.Data) -> None:
        await self._input_queue.put(ConversationMessageCreateEvent.model_validate({"data": data}))

    async def input_audio_buffer_append(self, data: InputAudioBufferAppendEvent.Data) -> None:
        await self._input_queue.put(InputAudioBufferAppendEvent.model_validate({"data": data}))

    async def input_audio_buffer_complete(self) -> None:
        await self._input_queue.put(InputAudioBufferCompleteEvent.model_validate({}))


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
        **kwargs,
    ) -> AsyncWebsocketsChatClient:
        return AsyncWebsocketsChatClient(
            base_url=self._base_url,
            requester=self._requester,
            bot_id=bot_id,
            on_event=on_event,  # type: ignore
            workflow_id=workflow_id,
            **kwargs,
        )
