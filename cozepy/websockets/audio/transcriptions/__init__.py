import base64
from typing import Callable, Dict, Optional, Union

from pydantic import BaseModel, field_serializer

from cozepy.request import Requester
from cozepy.util import dump_exclude_none, remove_url_trailing_slash
from cozepy.websockets.ws import (
    AsyncWebsocketsBaseClient,
    AsyncWebsocketsBaseEventHandler,
    InputAudio,
    WebsocketsBaseClient,
    WebsocketsBaseEventHandler,
    WebsocketsEvent,
    WebsocketsEventFactory,
    WebsocketsEventType,
)


# req
class TranscriptionsUpdateEvent(WebsocketsEvent):
    """更新语音识别配置

    更新语音识别配置。若更新成功，会收到 transcriptions.updated 的下行事件，否则，会收到 error 下行事件。
    docs: https://www.coze.cn/open/docs/developer_guides/asr_event#a7ca67ab
    """

    class Data(BaseModel):
        # 输入音频格式。
        input_audio: Optional[InputAudio] = None

    event_type: WebsocketsEventType = WebsocketsEventType.TRANSCRIPTIONS_UPDATE
    data: Data


# req
class InputAudioBufferAppendEvent(WebsocketsEvent):
    """流式上传音频片段

    流式向服务端提交音频的片段。
    docs: https://www.coze.cn/open/docs/developer_guides/asr_event#9ef6e6ca
    """

    class Data(BaseModel):
        # 音频片段。(API 返回的是base64编码的音频片段, SDK 已经自动解码为 bytes)
        delta: bytes

        @field_serializer("delta")
        def serialize_delta(self, delta: bytes, _info):
            return base64.b64encode(delta)

    event_type: WebsocketsEventType = WebsocketsEventType.INPUT_AUDIO_BUFFER_APPEND
    data: Data

    def _dump_without_delta(self):
        return dump_exclude_none(
            {
                "id": self.id,
                "type": self.event_type.value,
                "detail": self.detail,
                "data": {
                    "delta": f"<length: {len(self.data.delta) if self.data and self.data.delta else 0}>",
                },
            }
        )


# req
class InputAudioBufferCompleteEvent(WebsocketsEvent):
    """提交音频

    客户端发送 input_audio_buffer.complete 事件来告诉服务端提交音频缓冲区的数据。服务端提交成功后会返回 input_audio_buffer.completed 事件。
    docs: https://www.coze.cn/open/docs/developer_guides/asr_event#f5d76c87
    """

    event_type: WebsocketsEventType = WebsocketsEventType.INPUT_AUDIO_BUFFER_COMPLETE


# req
class InputAudioBufferClearEvent(WebsocketsEvent):
    """清除缓冲区音频

    客户端发送 input_audio_buffer.clear 事件来告诉服务端清除缓冲区的音频数据。服务端清除完后将返回 input_audio_buffer.cleared 事件。
    docs: https://www.coze.cn/open/docs/developer_guides/asr_event#e98db543
    """

    event_type: WebsocketsEventType = WebsocketsEventType.INPUT_AUDIO_BUFFER_CLEAR


# resp
class TranscriptionsCreatedEvent(WebsocketsEvent):
    """语音识别连接成功

    语音识别连接成功后，返回此事件。
    docs: https://www.coze.cn/open/docs/developer_guides/asr_event#06d772a3
    """

    event_type: WebsocketsEventType = WebsocketsEventType.TRANSCRIPTIONS_CREATED


# resp
class TranscriptionsUpdatedEvent(WebsocketsEvent):
    """配置更新成功

    配置更新成功后，会返回最新的配置。
    docs: https://www.coze.cn/open/docs/developer_guides/asr_event#3f842df1
    """

    class Data(BaseModel):
        # 输入音频格式。
        input_audio: Optional[InputAudio] = None

    event_type: WebsocketsEventType = WebsocketsEventType.TRANSCRIPTIONS_UPDATED
    data: Data


# resp
class InputAudioBufferCompletedEvent(WebsocketsEvent):
    """音频提交完成

    客户端发送 input_audio_buffer.complete 事件来告诉服务端提交音频缓冲区的数据。服务端提交成功后会返回 input_audio_buffer.completed 事件。
    docs: https://www.coze.cn/open/docs/developer_guides/asr_event#8d747148
    """

    event_type: WebsocketsEventType = WebsocketsEventType.INPUT_AUDIO_BUFFER_COMPLETED


# resp
class InputAudioBufferClearedEvent(WebsocketsEvent):
    """音频清除成功

    客户端发送 input_audio_buffer.clear 事件来告诉服务端清除音频缓冲区的数据。服务端清除完后将返回 input_audio_buffer.cleared 事件。
    docs: https://www.coze.cn/open/docs/developer_guides/asr_event#8211875b
    """

    event_type: WebsocketsEventType = WebsocketsEventType.INPUT_AUDIO_BUFFER_CLEARED


# resp
class TranscriptionsMessageUpdateEvent(WebsocketsEvent):
    """识别出文字

    语音识别出文字后，返回此事件，每次都返回全量的识别出来的文字。
    docs: https://www.coze.cn/open/docs/developer_guides/asr_event#772e6d2d
    """

    class Data(BaseModel):
        # 识别出的文字。
        content: str

    event_type: WebsocketsEventType = WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_UPDATE
    data: Data


# resp
class TranscriptionsMessageCompletedEvent(WebsocketsEvent):
    """识别完成

    语音识别完成后，返回此事件。
    docs: https://www.coze.cn/open/docs/developer_guides/asr_event#0c36158c
    """

    event_type: WebsocketsEventType = WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_COMPLETED


_audio_transcriptions_event_factory = WebsocketsEventFactory(
    {
        WebsocketsEventType.TRANSCRIPTIONS_CREATED.value: TranscriptionsCreatedEvent,
        WebsocketsEventType.TRANSCRIPTIONS_UPDATED.value: TranscriptionsUpdatedEvent,
        WebsocketsEventType.INPUT_AUDIO_BUFFER_COMPLETED.value: InputAudioBufferCompletedEvent,
        WebsocketsEventType.INPUT_AUDIO_BUFFER_CLEARED.value: InputAudioBufferClearedEvent,
        WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_UPDATE.value: TranscriptionsMessageUpdateEvent,
        WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_COMPLETED.value: TranscriptionsMessageCompletedEvent,
    }
)


class WebsocketsAudioTranscriptionsEventHandler(WebsocketsBaseEventHandler):
    # 连接成功
    def on_transcriptions_created(self, cli: "WebsocketsAudioTranscriptionsClient", event: TranscriptionsCreatedEvent):
        pass

    # 配置更新成功
    def on_transcriptions_updated(self, cli: "WebsocketsAudioTranscriptionsClient", event: TranscriptionsUpdatedEvent):
        pass

    # 音频提交完成
    def on_input_audio_buffer_completed(
        self, cli: "WebsocketsAudioTranscriptionsClient", event: InputAudioBufferCompletedEvent
    ):
        pass

    # 音频清除成功
    def on_input_audio_buffer_cleared(
        self, cli: "WebsocketsAudioTranscriptionsClient", event: InputAudioBufferClearedEvent
    ):
        pass

    # 识别出文字
    def on_transcriptions_message_update(
        self, cli: "WebsocketsAudioTranscriptionsClient", event: TranscriptionsMessageUpdateEvent
    ):
        pass

    # 识别完成
    def on_transcriptions_message_completed(
        self, cli: "WebsocketsAudioTranscriptionsClient", event: TranscriptionsMessageCompletedEvent
    ):
        pass


class WebsocketsAudioTranscriptionsClient(WebsocketsBaseClient):
    def __init__(
        self,
        base_url: str,
        requester: Requester,
        on_event: Union[WebsocketsAudioTranscriptionsEventHandler, Dict[WebsocketsEventType, Callable]],
        **kwargs,
    ):
        if isinstance(on_event, WebsocketsAudioTranscriptionsEventHandler):
            on_event = on_event.to_dict()
        super().__init__(
            base_url=base_url,
            requester=requester,
            path="v1/audio/transcriptions",
            event_factory=_audio_transcriptions_event_factory,
            on_event=on_event,  # type: ignore
            wait_events=[WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_COMPLETED],
            **kwargs,
        )

    # 更新语音识别配置
    def transcriptions_update(self, data: TranscriptionsUpdateEvent.Data) -> None:
        self._input_queue.put(TranscriptionsUpdateEvent.model_validate({"data": data}))

    # 流式上传音频片段
    def input_audio_buffer_append(self, data: InputAudioBufferAppendEvent.Data) -> None:
        self._input_queue.put(InputAudioBufferAppendEvent.model_validate({"data": data}))

    # 提交音频
    def input_audio_buffer_complete(self) -> None:
        self._input_queue.put(InputAudioBufferCompleteEvent.model_validate({}))

    # 清除缓冲区音频
    def input_audio_buffer_clear(self) -> None:
        self._input_queue.put(InputAudioBufferClearEvent.model_validate({}))


class WebsocketsAudioTranscriptionsBuildClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(
        self,
        *,
        on_event: Union[WebsocketsAudioTranscriptionsEventHandler, Dict[WebsocketsEventType, Callable]],
        **kwargs,
    ) -> WebsocketsAudioTranscriptionsClient:
        return WebsocketsAudioTranscriptionsClient(
            base_url=self._base_url,
            requester=self._requester,
            on_event=on_event,  # type: ignore
            **kwargs,
        )


class AsyncWebsocketsAudioTranscriptionsEventHandler(AsyncWebsocketsBaseEventHandler):
    # 连接成功
    async def on_transcriptions_created(
        self, cli: "AsyncWebsocketsAudioTranscriptionsClient", event: TranscriptionsCreatedEvent
    ):
        pass

    # 配置更新成功
    async def on_transcriptions_updated(
        self, cli: "AsyncWebsocketsAudioTranscriptionsClient", event: TranscriptionsUpdatedEvent
    ):
        pass

    # 音频提交完成
    async def on_input_audio_buffer_completed(
        self, cli: "AsyncWebsocketsAudioTranscriptionsClient", event: InputAudioBufferCompletedEvent
    ):
        pass

    # 音频清除成功
    async def on_input_audio_buffer_cleared(
        self, cli: "AsyncWebsocketsAudioTranscriptionsClient", event: InputAudioBufferClearedEvent
    ):
        pass

    # 识别出文字
    async def on_transcriptions_message_update(
        self, cli: "AsyncWebsocketsAudioTranscriptionsClient", event: TranscriptionsMessageUpdateEvent
    ):
        pass

    # 识别完成
    async def on_transcriptions_message_completed(
        self, cli: "AsyncWebsocketsAudioTranscriptionsClient", event: TranscriptionsMessageCompletedEvent
    ):
        pass


class AsyncWebsocketsAudioTranscriptionsClient(AsyncWebsocketsBaseClient):
    def __init__(
        self,
        base_url: str,
        requester: Requester,
        on_event: Union[AsyncWebsocketsAudioTranscriptionsEventHandler, Dict[WebsocketsEventType, Callable]],
        **kwargs,
    ):
        if isinstance(on_event, AsyncWebsocketsAudioTranscriptionsEventHandler):
            on_event = on_event.to_dict()
        super().__init__(
            base_url=base_url,
            requester=requester,
            path="v1/audio/transcriptions",
            event_factory=_audio_transcriptions_event_factory,
            on_event=on_event,  # type: ignore
            wait_events=[WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_COMPLETED],
            **kwargs,
        )

    # 更新语音识别配置
    async def transcriptions_update(self, data: TranscriptionsUpdateEvent.Data) -> None:
        await self._input_queue.put(TranscriptionsUpdateEvent.model_validate({"data": data}))

    # 流式上传音频片段
    async def input_audio_buffer_append(self, data: InputAudioBufferAppendEvent.Data) -> None:
        await self._input_queue.put(InputAudioBufferAppendEvent.model_validate({"data": data}))

    # 提交音频
    async def input_audio_buffer_complete(self) -> None:
        await self._input_queue.put(InputAudioBufferCompleteEvent.model_validate({}))

    # 清除缓冲区音频
    async def input_audio_buffer_clear(self) -> None:
        await self._input_queue.put(InputAudioBufferClearEvent.model_validate({}))


class AsyncWebsocketsAudioTranscriptionsBuildClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(
        self,
        *,
        on_event: Union[AsyncWebsocketsAudioTranscriptionsEventHandler, Dict[WebsocketsEventType, Callable]],
        **kwargs,
    ) -> AsyncWebsocketsAudioTranscriptionsClient:
        return AsyncWebsocketsAudioTranscriptionsClient(
            base_url=self._base_url,
            requester=self._requester,
            on_event=on_event,  # type: ignore
            **kwargs,
        )
