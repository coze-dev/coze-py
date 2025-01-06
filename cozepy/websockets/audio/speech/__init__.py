import base64
from typing import Callable, Dict, Optional, Union

from pydantic import BaseModel, field_serializer

from cozepy.auth import Auth
from cozepy.log import log_warning
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash
from cozepy.websockets.ws import (
    AsyncWebsocketsBaseClient,
    AsyncWebsocketsBaseEventHandler,
    WebsocketsEvent,
    WebsocketsEventType,
)


# req
class InputTextBufferAppendEvent(WebsocketsEvent):
    class Data(BaseModel):
        delta: str

    type: WebsocketsEventType = WebsocketsEventType.INPUT_TEXT_BUFFER_APPEND
    data: Data


# req
class InputTextBufferCommitEvent(WebsocketsEvent):
    type: WebsocketsEventType = WebsocketsEventType.INPUT_TEXT_BUFFER_COMMIT


# req
class SpeechUpdateEvent(WebsocketsEvent):
    class OpusConfig(object):
        bitrate: Optional[int] = None
        use_cbr: Optional[bool] = None
        frame_size_ms: Optional[float] = None

    class PCMConfig(object):
        sample_rate: Optional[int] = None

    class OutputAudio(object):
        codec: Optional[str]
        pcm_config: Optional["SpeechUpdateEvent.PCMConfig"]
        opus_config: Optional["SpeechUpdateEvent.OpusConfig"]
        speech_rate: Optional[int]
        voice_id: Optional[str]

    class Data:
        output_audio: "SpeechUpdateEvent.OutputAudio"

    type: WebsocketsEventType = WebsocketsEventType.SPEECH_UPDATE
    data: Data


# resp
class InputTextBufferCommittedEvent(WebsocketsEvent):
    type: WebsocketsEventType = WebsocketsEventType.INPUT_TEXT_BUFFER_COMMITTED


# resp
class SpeechAudioUpdateEvent(WebsocketsEvent):
    class Data(BaseModel):
        delta: bytes

        @field_serializer("delta")
        def serialize_delta(self, delta: bytes, _info):
            return base64.b64encode(delta)

    type: WebsocketsEventType = WebsocketsEventType.SPEECH_AUDIO_UPDATE
    data: Data


# resp
class SpeechAudioCompletedEvent(WebsocketsEvent):
    type: WebsocketsEventType = WebsocketsEventType.SPEECH_AUDIO_COMPLETED


class AsyncWebsocketsAudioSpeechEventHandler(AsyncWebsocketsBaseEventHandler):
    async def on_input_text_buffer_committed(
        self, cli: "AsyncWebsocketsAudioSpeechEventHandler", event: InputTextBufferCommittedEvent
    ):
        pass

    async def on_speech_audio_update(
        self, cli: "AsyncWebsocketsAudioSpeechEventHandler", event: SpeechAudioUpdateEvent
    ):
        pass

    async def on_speech_audio_completed(
        self, cli: "AsyncWebsocketsAudioSpeechEventHandler", event: SpeechAudioCompletedEvent
    ):
        pass


class AsyncWebsocketsAudioSpeechCreateClient(AsyncWebsocketsBaseClient):
    def __init__(
        self,
        base_url: str,
        auth: Auth,
        requester: Requester,
        on_event: Union[AsyncWebsocketsAudioSpeechEventHandler, Dict[WebsocketsEventType, Callable]],
        **kwargs,
    ):
        if isinstance(on_event, AsyncWebsocketsAudioSpeechEventHandler):
            on_event = {
                WebsocketsEventType.ERROR: on_event.on_error,
                WebsocketsEventType.CLOSED: on_event.on_closed,
                WebsocketsEventType.INPUT_TEXT_BUFFER_COMMITTED: on_event.on_input_text_buffer_committed,
                WebsocketsEventType.SPEECH_AUDIO_UPDATE: on_event.on_speech_audio_update,
                WebsocketsEventType.SPEECH_AUDIO_COMPLETED: on_event.on_speech_audio_completed,
            }
        super().__init__(
            base_url=base_url,
            auth=auth,
            requester=requester,
            path="v1/audio/speech",
            on_event=on_event,
            wait_events=[WebsocketsEventType.SPEECH_AUDIO_COMPLETED],
            **kwargs,
        )

    async def append(self, text: str) -> None:
        await self._input_queue.put(
            InputTextBufferAppendEvent.model_validate(
                {
                    "data": InputTextBufferAppendEvent.Data.model_validate(
                        {
                            "delta": text,
                        }
                    )
                }
            )
        )

    async def commit(self) -> None:
        await self._input_queue.put(InputTextBufferCommitEvent.model_validate({}))

    async def update(self, event: SpeechUpdateEvent) -> None:
        await self._input_queue.put(event)

    def _load_event(self, message: Dict) -> Optional[WebsocketsEvent]:
        event_id = message.get("event_id") or ""
        event_type = message.get("type") or ""
        data = message.get("data") or {}
        if event_type == WebsocketsEventType.INPUT_TEXT_BUFFER_COMMITTED:
            return InputTextBufferCommittedEvent.model_validate({"event_id": event_id})
        if event_type == WebsocketsEventType.SPEECH_AUDIO_UPDATE.value:
            delta_base64 = data.get("delta")
            if delta_base64 is None:
                raise ValueError("Missing 'delta' in event data")
            return SpeechAudioUpdateEvent.model_validate(
                {
                    "event_id": event_id,
                    "data": SpeechAudioUpdateEvent.Data.model_validate(
                        {
                            "delta": base64.b64decode(delta_base64),
                        }
                    ),
                }
            )
        elif event_type == WebsocketsEventType.SPEECH_AUDIO_COMPLETED.value:
            return SpeechAudioCompletedEvent.model_validate({"event_id": event_id})
        else:
            log_warning("[%s] unknown event=%s", self._path, event_type)
        return None


class AsyncWebsocketsAudioSpeechClient:
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._auth = auth
        self._requester = requester

    def create(
        self, *, on_event: Union[AsyncWebsocketsAudioSpeechEventHandler, Dict[WebsocketsEventType, Callable]], **kwargs
    ) -> AsyncWebsocketsAudioSpeechCreateClient:
        return AsyncWebsocketsAudioSpeechCreateClient(
            base_url=self._base_url,
            auth=self._auth,
            requester=self._requester,
            on_event=on_event,
            **kwargs,
        )
