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
    WebsocketsBaseClient,
    WebsocketsBaseEventHandler,
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
class InputTextBufferCompleteEvent(WebsocketsEvent):
    type: WebsocketsEventType = WebsocketsEventType.INPUT_TEXT_BUFFER_COMPLETE


# req
class SpeechUpdateEvent(WebsocketsEvent):
    class OpusConfig(BaseModel):
        bitrate: Optional[int] = None
        use_cbr: Optional[bool] = None
        frame_size_ms: Optional[float] = None

    class PCMConfig(BaseModel):
        sample_rate: Optional[int] = None

    class OutputAudio(BaseModel):
        codec: Optional[str]
        pcm_config: Optional["SpeechUpdateEvent.PCMConfig"] = None
        opus_config: Optional["SpeechUpdateEvent.OpusConfig"] = None
        speech_rate: Optional[int] = None
        voice_id: Optional[str] = None

    class Data(BaseModel):
        output_audio: "SpeechUpdateEvent.OutputAudio"

    type: WebsocketsEventType = WebsocketsEventType.SPEECH_UPDATE
    data: Data


# resp
class InputTextBufferCompletedEvent(WebsocketsEvent):
    type: WebsocketsEventType = WebsocketsEventType.INPUT_TEXT_BUFFER_COMPLETED


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


class WebsocketsAudioSpeechEventHandler(WebsocketsBaseEventHandler):
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
        auth: Auth,
        requester: Requester,
        on_event: Union[WebsocketsAudioSpeechEventHandler, Dict[WebsocketsEventType, Callable]],
        **kwargs,
    ):
        if isinstance(on_event, WebsocketsAudioSpeechEventHandler):
            on_event = on_event.to_dict(
                {
                    WebsocketsEventType.INPUT_TEXT_BUFFER_COMPLETED: on_event.on_input_text_buffer_completed,
                    WebsocketsEventType.SPEECH_AUDIO_UPDATE: on_event.on_speech_audio_update,
                    WebsocketsEventType.SPEECH_AUDIO_COMPLETED: on_event.on_speech_audio_completed,
                }
            )
        super().__init__(
            base_url=base_url,
            auth=auth,
            requester=requester,
            path="v1/audio/speech",
            on_event=on_event,
            wait_events=[WebsocketsEventType.SPEECH_AUDIO_COMPLETED],
            **kwargs,
        )

    def input_text_buffer_append(self, data: InputTextBufferAppendEvent) -> None:
        self._input_queue.put(InputTextBufferAppendEvent.model_validate({"data": data}))

    def input_text_buffer_complete(self) -> None:
        self._input_queue.put(InputTextBufferCompleteEvent.model_validate({}))

    def speech_update(self, event: SpeechUpdateEvent) -> None:
        self._input_queue.put(event)

    def _load_event(self, message: Dict) -> Optional[WebsocketsEvent]:
        event_id = message.get("event_id") or ""
        logid = message.get("logid") or ""
        event_type = message.get("type") or ""
        data = message.get("data") or {}
        if event_type == WebsocketsEventType.INPUT_TEXT_BUFFER_COMPLETED:
            return InputTextBufferCompletedEvent.model_validate(
                {
                    "event_id": event_id,
                    "logid": logid,
                }
            )
        if event_type == WebsocketsEventType.SPEECH_AUDIO_UPDATE.value:
            delta_base64 = data.get("delta")
            if delta_base64 is None:
                raise ValueError("Missing 'delta' in event data")
            return SpeechAudioUpdateEvent.model_validate(
                {
                    "event_id": event_id,
                    "logid": logid,
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
                    "event_id": event_id,
                    "logid": logid,
                }
            )
        else:
            log_warning("[%s] unknown event, type=%s, logid=%s", self._path, event_type, logid)
        return None


class WebsocketsAudioSpeechBuildClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._auth = auth
        self._requester = requester

    def create(
        self, *, on_event: Union[WebsocketsAudioSpeechEventHandler, Dict[WebsocketsEventType, Callable]], **kwargs
    ) -> WebsocketsAudioSpeechClient:
        return WebsocketsAudioSpeechClient(
            base_url=self._base_url,
            auth=self._auth,
            requester=self._requester,
            on_event=on_event,
            **kwargs,
        )


class AsyncWebsocketsAudioSpeechEventHandler(AsyncWebsocketsBaseEventHandler):
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
    class EventHandler(AsyncWebsocketsBaseEventHandler):
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

    def __init__(
        self,
        base_url: str,
        auth: Auth,
        requester: Requester,
        on_event: Union["AsyncWebsocketsAudioSpeechClient.EventHandler", Dict[WebsocketsEventType, Callable]],
        **kwargs,
    ):
        if isinstance(on_event, AsyncWebsocketsAudioSpeechClient.EventHandler):
            on_event = on_event.to_dict(
                {
                    WebsocketsEventType.INPUT_TEXT_BUFFER_COMPLETED: on_event.on_input_text_buffer_completed,
                    WebsocketsEventType.SPEECH_AUDIO_UPDATE: on_event.on_speech_audio_update,
                    WebsocketsEventType.SPEECH_AUDIO_COMPLETED: on_event.on_speech_audio_completed,
                }
            )
        super().__init__(
            base_url=base_url,
            auth=auth,
            requester=requester,
            path="v1/audio/speech",
            on_event=on_event,
            wait_events=[WebsocketsEventType.SPEECH_AUDIO_COMPLETED],
            **kwargs,
        )

    async def input_text_buffer_append(self, data: InputTextBufferAppendEvent) -> None:
        await self._input_queue.put(InputTextBufferAppendEvent.model_validate({"data": data}))

    async def input_text_buffer_complete(self) -> None:
        await self._input_queue.put(InputTextBufferCompleteEvent.model_validate({}))

    async def speech_update(self, data: SpeechUpdateEvent.Data) -> None:
        await self._input_queue.put(SpeechUpdateEvent.model_validate({"data": data}))

    def _load_event(self, message: Dict) -> Optional[WebsocketsEvent]:
        event_id = message.get("event_id") or ""
        logid = message.get("logid") or ""
        event_type = message.get("type") or ""
        data = message.get("data") or {}
        if event_type == WebsocketsEventType.INPUT_TEXT_BUFFER_COMPLETED:
            return InputTextBufferCompletedEvent.model_validate({"event_id": event_id, "logid": logid})
        if event_type == WebsocketsEventType.SPEECH_AUDIO_UPDATE.value:
            delta_base64 = data.get("delta")
            if delta_base64 is None:
                raise ValueError("Missing 'delta' in event data")
            return SpeechAudioUpdateEvent.model_validate(
                {
                    "event_id": event_id,
                    "logid": logid,
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
                    "event_id": event_id,
                    "logid": logid,
                }
            )
        else:
            log_warning("[%s] unknown event, type=%s, logid=%s", self._path, event_type, logid)
        return None


class AsyncWebsocketsAudioSpeechBuildClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._auth = auth
        self._requester = requester

    def create(
        self,
        *,
        on_event: Union[AsyncWebsocketsAudioSpeechClient.EventHandler, Dict[WebsocketsEventType, Callable]],
        **kwargs,
    ) -> AsyncWebsocketsAudioSpeechClient:
        return AsyncWebsocketsAudioSpeechClient(
            base_url=self._base_url,
            auth=self._auth,
            requester=self._requester,
            on_event=on_event,
            **kwargs,
        )
