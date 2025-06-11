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
    class Data(BaseModel):
        delta: str

    event_type: WebsocketsEventType = WebsocketsEventType.INPUT_TEXT_BUFFER_APPEND
    data: Data


# req
class InputTextBufferCompleteEvent(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.INPUT_TEXT_BUFFER_COMPLETE


# req
class SpeechUpdateEvent(WebsocketsEvent):
    class Data(BaseModel):
        output_audio: Optional[OutputAudio] = None

    event_type: WebsocketsEventType = WebsocketsEventType.SPEECH_UPDATE
    data: Data


# resp
class SpeechCreatedEvent(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.SPEECH_CREATED


# resp
class InputTextBufferCompletedEvent(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.INPUT_TEXT_BUFFER_COMPLETED


# resp
class SpeechAudioUpdateEvent(WebsocketsEvent):
    class Data(BaseModel):
        delta: bytes

        @field_serializer("delta")
        def serialize_delta(self, delta: bytes, _info):
            return base64.b64encode(delta)

        @field_validator("delta")
        @classmethod
        def validate_delta(cls, delta: bytes):
            return base64.b64decode(delta)

    event_type: WebsocketsEventType = WebsocketsEventType.SPEECH_AUDIO_UPDATE
    data: Data


# resp
class SpeechAudioCompletedEvent(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.SPEECH_AUDIO_COMPLETED


_audio_speech_event_factory = WebsocketsEventFactory(
    {
        WebsocketsEventType.SPEECH_CREATED.value: SpeechCreatedEvent,
        WebsocketsEventType.INPUT_TEXT_BUFFER_COMPLETED.value: InputTextBufferCompletedEvent,
        WebsocketsEventType.SPEECH_AUDIO_UPDATE.value: SpeechAudioUpdateEvent,
        WebsocketsEventType.SPEECH_AUDIO_COMPLETED.value: SpeechAudioCompletedEvent,
    }
)


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
            event_factory=_audio_speech_event_factory,
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
            event_factory=_audio_speech_event_factory,
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
