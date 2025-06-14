import base64
from typing import Callable, Dict, Optional, Union

from pydantic import BaseModel, field_serializer, field_validator

from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash
from cozepy.websockets.ws import (
    AsyncWebsocketsBaseClient,
    AsyncWebsocketsBaseEventHandler,
    OutputAudio,
    WebsocketsBaseClient,
    WebsocketsBaseEventHandler,
    WebsocketsEvent,
    WebsocketsEventFactory,
    WebsocketsEventType,
)


# req
class InputTextBufferAppendEvent(WebsocketsEvent):
    """流式输入文字

    流式向服务端提交文字的片段。
    docs: https://www.coze.cn/open/docs/developer_guides/tts_event#0ba93be3
    """

    class Data(BaseModel):
        # 需要合成语音的文字片段。
        delta: str

    event_type: WebsocketsEventType = WebsocketsEventType.INPUT_TEXT_BUFFER_APPEND
    data: Data


# req
class InputTextBufferCompleteEvent(WebsocketsEvent):
    """提交文字

    提交 append 的文本，发送后将收到 input_text_buffer.completed 的下行事件。
    docs: https://www.coze.cn/open/docs/developer_guides/tts_event#ab24ada9
    """

    event_type: WebsocketsEventType = WebsocketsEventType.INPUT_TEXT_BUFFER_COMPLETE


# req
class SpeechUpdateEvent(WebsocketsEvent):
    """更新语音合成配置

    更新流式语音合成配置。
    docs: https://www.coze.cn/open/docs/developer_guides/tts_event#6166c24c
    """

    class Data(BaseModel):
        # 输出音频格式。
        output_audio: Optional[OutputAudio] = None

    event_type: WebsocketsEventType = WebsocketsEventType.SPEECH_UPDATE
    data: Data


# resp
class SpeechCreatedEvent(WebsocketsEvent):
    """语音合成连接成功

    语音合成连接成功后，返回此事件。
    docs: https://www.coze.cn/open/docs/developer_guides/tts_event#23c0993e
    """

    event_type: WebsocketsEventType = WebsocketsEventType.SPEECH_CREATED


# resp
class SpeechUpdatedEvent(WebsocketsEvent):
    """配置更新完成

    配置更新成功后，会返回最新的配置。
    docs: https://www.coze.cn/open/docs/developer_guides/tts_event#a3a59fb4
    """

    class Data(BaseModel):
        # 输出音频格式。
        output_audio: Optional[OutputAudio] = None

    event_type: WebsocketsEventType = WebsocketsEventType.SPEECH_UPDATED
    data: Data


# resp
class InputTextBufferCompletedEvent(WebsocketsEvent):
    """input_text_buffer 提交完成

    流式提交的文字完成后，返回此事件。
    docs: https://www.coze.cn/open/docs/developer_guides/tts_event#cf5e0495
    """

    event_type: WebsocketsEventType = WebsocketsEventType.INPUT_TEXT_BUFFER_COMPLETED


# resp
class SpeechAudioUpdateEvent(WebsocketsEvent):
    """合成增量语音

    语音合成产生增量语音时，返回此事件。
    docs: https://www.coze.cn/open/docs/developer_guides/tts_event#98163c71
    """

    class Data(BaseModel):
        # 音频片段。(API 返回的是base64编码的音频片段, SDK 已经自动解码为 bytes)
        delta: bytes

        @field_serializer("delta")
        def serialize_delta(self, delta: bytes, _info):
            return base64.b64encode(delta)

        @field_validator("delta", mode="before")
        @classmethod
        def validate_delta(cls, delta: str):
            return base64.b64decode(delta)

    event_type: WebsocketsEventType = WebsocketsEventType.SPEECH_AUDIO_UPDATE
    data: Data


# resp
class SpeechAudioCompletedEvent(WebsocketsEvent):
    """合成完成

    语音合成完成后，返回此事件。
    docs: https://www.coze.cn/open/docs/developer_guides/tts_event#f42e9cb7
    """

    event_type: WebsocketsEventType = WebsocketsEventType.SPEECH_AUDIO_COMPLETED


_audio_speech_event_factory = WebsocketsEventFactory(
    {
        WebsocketsEventType.SPEECH_CREATED.value: SpeechCreatedEvent,
        WebsocketsEventType.SPEECH_UPDATED.value: SpeechUpdatedEvent,
        WebsocketsEventType.INPUT_TEXT_BUFFER_COMPLETED.value: InputTextBufferCompletedEvent,
        WebsocketsEventType.SPEECH_AUDIO_UPDATE.value: SpeechAudioUpdateEvent,
        WebsocketsEventType.SPEECH_AUDIO_COMPLETED.value: SpeechAudioCompletedEvent,
    }
)


class WebsocketsAudioSpeechEventHandler(WebsocketsBaseEventHandler):
    # 语音合成连接成功
    def on_speech_created(self, cli: "WebsocketsAudioSpeechClient", event: SpeechCreatedEvent):
        pass

    # 配置更新完成
    def on_speech_updated(self, cli: "WebsocketsAudioSpeechClient", event: SpeechUpdatedEvent):
        pass

    # input_text_buffer 提交完成
    def on_input_text_buffer_completed(self, cli: "WebsocketsAudioSpeechClient", event: InputTextBufferCompletedEvent):
        pass

    # 合成增量语音
    def on_speech_audio_update(self, cli: "WebsocketsAudioSpeechClient", event: SpeechAudioUpdateEvent):
        pass

    # 合成完成
    def on_speech_audio_completed(self, cli: "WebsocketsAudioSpeechClient", event: SpeechAudioCompletedEvent):
        pass


class WebsocketsAudioSpeechClient(WebsocketsBaseClient):
    def __init__(
        self,
        base_url: str,
        requester: Requester,
        on_event: Union[WebsocketsAudioSpeechEventHandler, Dict[WebsocketsEventType, Callable]],
        **kwargs,
    ):
        if isinstance(on_event, WebsocketsAudioSpeechEventHandler):
            on_event = on_event.to_dict()
        super().__init__(
            base_url=base_url,
            requester=requester,
            path="v1/audio/speech",
            event_factory=_audio_speech_event_factory,
            on_event=on_event,  # type: ignore
            wait_events=[WebsocketsEventType.SPEECH_AUDIO_COMPLETED],
            **kwargs,
        )

    # 更新语音合成配置
    def speech_update(self, event: SpeechUpdateEvent) -> None:
        self._input_queue.put(event)

    # 流式输入文字
    def input_text_buffer_append(self, data: InputTextBufferAppendEvent.Data) -> None:
        self._input_queue.put(InputTextBufferAppendEvent.model_validate({"data": data}))

    # 提交文字
    def input_text_buffer_complete(self) -> None:
        self._input_queue.put(InputTextBufferCompleteEvent.model_validate({}))


class WebsocketsAudioSpeechBuildClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(
        self, *, on_event: Union[WebsocketsAudioSpeechEventHandler, Dict[WebsocketsEventType, Callable]], **kwargs
    ) -> WebsocketsAudioSpeechClient:
        return WebsocketsAudioSpeechClient(
            base_url=self._base_url,
            requester=self._requester,
            on_event=on_event,  # type: ignore
            **kwargs,
        )


class AsyncWebsocketsAudioSpeechEventHandler(AsyncWebsocketsBaseEventHandler):
    # 语音合成连接成功
    async def on_speech_created(self, cli: "AsyncWebsocketsAudioSpeechClient", event: SpeechCreatedEvent):
        pass

    # 配置更新完成
    async def on_speech_updated(self, cli: "AsyncWebsocketsAudioSpeechClient", event: SpeechUpdatedEvent):
        pass

    # input_text_buffer 提交完成
    async def on_input_text_buffer_completed(
        self, cli: "AsyncWebsocketsAudioSpeechClient", event: InputTextBufferCompletedEvent
    ):
        pass

    # 合成增量语音
    async def on_speech_audio_update(self, cli: "AsyncWebsocketsAudioSpeechClient", event: SpeechAudioUpdateEvent):
        pass

    # 合成完成
    async def on_speech_audio_completed(
        self, cli: "AsyncWebsocketsAudioSpeechClient", event: SpeechAudioCompletedEvent
    ):
        pass


class AsyncWebsocketsAudioSpeechClient(AsyncWebsocketsBaseClient):
    def __init__(
        self,
        base_url: str,
        requester: Requester,
        on_event: Union[AsyncWebsocketsAudioSpeechEventHandler, Dict[WebsocketsEventType, Callable]],
        **kwargs,
    ):
        if isinstance(on_event, AsyncWebsocketsAudioSpeechEventHandler):
            on_event = on_event.to_dict()
        super().__init__(
            base_url=base_url,
            requester=requester,
            path="v1/audio/speech",
            event_factory=_audio_speech_event_factory,
            on_event=on_event,  # type: ignore
            wait_events=[WebsocketsEventType.SPEECH_AUDIO_COMPLETED],
            **kwargs,
        )

    # 更新语音合成配置
    async def speech_update(self, event: SpeechUpdateEvent) -> None:
        await self._input_queue.put(event)

    # 流式输入文字
    async def input_text_buffer_append(self, data: InputTextBufferAppendEvent.Data) -> None:
        await self._input_queue.put(InputTextBufferAppendEvent.model_validate({"data": data}))

    # 提交文字
    async def input_text_buffer_complete(self) -> None:
        await self._input_queue.put(InputTextBufferCompleteEvent.model_validate({}))


class AsyncWebsocketsAudioSpeechBuildClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(
        self,
        *,
        on_event: Union[AsyncWebsocketsAudioSpeechEventHandler, Dict[WebsocketsEventType, Callable]],
        **kwargs,
    ) -> AsyncWebsocketsAudioSpeechClient:
        return AsyncWebsocketsAudioSpeechClient(
            base_url=self._base_url,
            requester=self._requester,
            on_event=on_event,  # type: ignore
            **kwargs,
        )
