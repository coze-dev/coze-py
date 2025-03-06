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

    event_type: WebsocketsEventType = WebsocketsEventType.SPEECH_AUDIO_UPDATE
    data: Data


# resp
class SpeechAudioCompletedEvent(WebsocketsEvent):
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
            on_event = on_event.to_dict(
                {
                    WebsocketsEventType.SPEECH_CREATED: on_event.on_speech_created,
                    WebsocketsEventType.INPUT_TEXT_BUFFER_COMPLETED: on_event.on_input_text_buffer_completed,
                    WebsocketsEventType.SPEECH_AUDIO_UPDATE: on_event.on_speech_audio_update,
                    WebsocketsEventType.SPEECH_AUDIO_COMPLETED: on_event.on_speech_audio_completed,
                }
            )
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
            on_event = on_event.to_dict(
                {
                    WebsocketsEventType.SPEECH_CREATED: on_event.on_speech_created,
                    WebsocketsEventType.INPUT_TEXT_BUFFER_COMPLETED: on_event.on_input_text_buffer_completed,
                    WebsocketsEventType.SPEECH_AUDIO_UPDATE: on_event.on_speech_audio_update,
                    WebsocketsEventType.SPEECH_AUDIO_COMPLETED: on_event.on_speech_audio_completed,
                }
            )
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
