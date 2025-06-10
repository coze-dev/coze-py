import base64
from typing import Callable, Dict, Optional, Union

from pydantic import BaseModel, field_serializer

from cozepy.log import log_warning
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash
from cozepy.websockets.ws import (
    AsyncWebsocketsBaseClient,
    AsyncWebsocketsBaseEventHandler,
    OutputAudio,
    WebsocketsBaseClient,
    WebsocketsBaseEventHandler,
    WebsocketsEvent,
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

    event_type: WebsocketsEventType = WebsocketsEventType.SPEECH_AUDIO_UPDATE
    data: Data


# resp
class SpeechAudioCompletedEvent(WebsocketsEvent):
    """合成完成

    语音合成完成后，返回此事件。
    docs: https://www.coze.cn/open/docs/developer_guides/tts_event#f42e9cb7
    """

    event_type: WebsocketsEventType = WebsocketsEventType.SPEECH_AUDIO_COMPLETED


class WebsocketsAudioSpeechEventHandler(WebsocketsBaseEventHandler):
    def on_speech_created(self, cli: "WebsocketsAudioSpeechClient", event: SpeechCreatedEvent):
        pass

    def on_input_text_buffer_completed(self, cli: "WebsocketsAudioSpeechClient", event: InputTextBufferCompletedEvent):
        pass

    def on_speech_audio_update(self, cli: "WebsocketsAudioSpeechClient", event: SpeechAudioUpdateEvent):
        pass

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
            on_event=on_event,  # type: ignore
            wait_events=[WebsocketsEventType.SPEECH_AUDIO_COMPLETED],
            **kwargs,
        )

    def input_text_buffer_append(self, data: InputTextBufferAppendEvent.Data) -> None:
        self._input_queue.put(InputTextBufferAppendEvent.model_validate({"data": data}))

    def input_text_buffer_complete(self) -> None:
        self._input_queue.put(InputTextBufferCompleteEvent.model_validate({}))

    def speech_update(self, event: SpeechUpdateEvent) -> None:
        self._input_queue.put(event)

    def _load_event(self, message: Dict) -> Optional[WebsocketsEvent]:
        event_id = message.get("id") or ""
        detail = WebsocketsEvent.Detail.model_validate(message.get("detail") or {})
        event_type = message.get("event_type") or ""
        data = message.get("data") or {}
        if event_type == WebsocketsEventType.SPEECH_CREATED:
            return SpeechCreatedEvent.model_validate({"id": event_id, "detail": detail})
        elif event_type == WebsocketsEventType.INPUT_TEXT_BUFFER_COMPLETED:
            return InputTextBufferCompletedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        elif event_type == WebsocketsEventType.SPEECH_AUDIO_UPDATE.value:
            delta_base64 = data.get("delta")
            if delta_base64 is None:
                raise ValueError("Missing 'delta' in event data")
            return SpeechAudioUpdateEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                    "data": SpeechAudioUpdateEvent.Data.model_validate(
                        {
                            "delta": base64.b64decode(delta_base64),
                        }
                    ),
                }
            )
        elif event_type == WebsocketsEventType.SPEECH_AUDIO_COMPLETED.value:
            return SpeechAudioCompletedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        else:
            log_warning("[%s] unknown event, type=%s, logid=%s", self._path, event_type, detail.logid)
        return None


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
    async def on_speech_created(self, cli: "AsyncWebsocketsAudioSpeechClient", event: SpeechCreatedEvent):
        pass

    async def on_input_text_buffer_completed(
        self, cli: "AsyncWebsocketsAudioSpeechClient", event: InputTextBufferCompletedEvent
    ):
        pass

    async def on_speech_audio_update(self, cli: "AsyncWebsocketsAudioSpeechClient", event: SpeechAudioUpdateEvent):
        pass

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
            on_event=on_event,  # type: ignore
            wait_events=[WebsocketsEventType.SPEECH_AUDIO_COMPLETED],
            **kwargs,
        )

    async def input_text_buffer_append(self, data: InputTextBufferAppendEvent.Data) -> None:
        await self._input_queue.put(InputTextBufferAppendEvent.model_validate({"data": data}))

    async def input_text_buffer_complete(self) -> None:
        await self._input_queue.put(InputTextBufferCompleteEvent.model_validate({}))

    async def speech_update(self, data: SpeechUpdateEvent.Data) -> None:
        await self._input_queue.put(SpeechUpdateEvent.model_validate({"data": data}))

    def _load_event(self, message: Dict) -> Optional[WebsocketsEvent]:
        event_id = message.get("id") or ""
        detail = WebsocketsEvent.Detail.model_validate(message.get("detail") or {})
        event_type = message.get("event_type") or ""
        data = message.get("data") or {}
        if event_type == WebsocketsEventType.SPEECH_CREATED:
            return SpeechCreatedEvent.model_validate({"id": event_id, "detail": detail})
        elif event_type == WebsocketsEventType.INPUT_TEXT_BUFFER_COMPLETED:
            return InputTextBufferCompletedEvent.model_validate({"id": event_id, "detail": detail})
        elif event_type == WebsocketsEventType.SPEECH_AUDIO_UPDATE.value:
            delta_base64 = data.get("delta")
            if delta_base64 is None:
                raise ValueError("Missing 'delta' in event data")
            return SpeechAudioUpdateEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                    "data": SpeechAudioUpdateEvent.Data.model_validate(
                        {
                            "delta": base64.b64decode(delta_base64),
                        }
                    ),
                }
            )
        elif event_type == WebsocketsEventType.SPEECH_AUDIO_COMPLETED.value:
            return SpeechAudioCompletedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        else:
            log_warning("[%s] unknown event, type=%s, logid=%s", self._path, event_type, detail.logid)
        return None


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
