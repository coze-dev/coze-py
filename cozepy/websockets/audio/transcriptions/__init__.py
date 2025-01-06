import base64
from typing import Callable, Dict, Optional, Union

from pydantic import BaseModel, field_serializer

from cozepy.auth import Auth
from cozepy.log import log_warning
from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash
from cozepy.websockets.ws import (
    AsyncWebsocketsBaseClient,
    AsyncWebsocketsBaseEventHandler,
    WebsocketsEvent,
    WebsocketsEventType,
)


# req
class InputAudioBufferAppendEvent(WebsocketsEvent):
    class Data(BaseModel):
        delta: bytes

        @field_serializer("delta")
        def serialize_delta(self, delta: bytes, _info):
            return base64.b64encode(delta)

    type: WebsocketsEventType = WebsocketsEventType.INPUT_AUDIO_BUFFER_APPEND
    data: Data


# req
class InputAudioBufferCommitEvent(WebsocketsEvent):
    type: WebsocketsEventType = WebsocketsEventType.INPUT_AUDIO_BUFFER_COMMIT


# req
class TranscriptionsUpdateEvent(WebsocketsEvent):
    class InputAudio(CozeModel):
        format: Optional[str]
        codec: Optional[str]
        sample_rate: Optional[int]
        channel: Optional[int]
        bit_depth: Optional[int]

    class Data(BaseModel):
        input_audio: "TranscriptionsUpdateEvent.InputAudio"

    type: WebsocketsEventType = WebsocketsEventType.TRANSCRIPTIONS_UPDATE
    data: Data


# resp
class InputAudioBufferCommittedEvent(WebsocketsEvent):
    type: WebsocketsEventType = WebsocketsEventType.INPUT_AUDIO_BUFFER_COMMITTED


# resp
class TranscriptionsMessageUpdateEvent(WebsocketsEvent):
    class Data(BaseModel):
        content: str

    type: WebsocketsEventType = WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_UPDATE
    data: Data


# resp
class TranscriptionsMessageCompletedEvent(WebsocketsEvent):
    type: WebsocketsEventType = WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_COMPLETED


class AsyncWebsocketsAudioTranscriptionsEventHandler(AsyncWebsocketsBaseEventHandler):
    async def on_input_audio_buffer_committed(
        self, cli: "AsyncWebsocketsAudioTranscriptionsCreateClient", event: InputAudioBufferCommittedEvent
    ):
        pass

    async def on_transcriptions_message_update(
        self, cli: "AsyncWebsocketsAudioTranscriptionsCreateClient", event: TranscriptionsMessageUpdateEvent
    ):
        pass

    async def on_transcriptions_message_completed(
        self, cli: "AsyncWebsocketsAudioTranscriptionsCreateClient", event: TranscriptionsMessageCompletedEvent
    ):
        pass


class AsyncWebsocketsAudioTranscriptionsCreateClient(AsyncWebsocketsBaseClient):
    def __init__(
        self,
        base_url: str,
        auth: Auth,
        requester: Requester,
        on_event: Union[AsyncWebsocketsAudioTranscriptionsEventHandler, Dict[WebsocketsEventType, Callable]],
        **kwargs,
    ):
        if isinstance(on_event, AsyncWebsocketsAudioTranscriptionsEventHandler):
            on_event = {
                WebsocketsEventType.ERROR: on_event.on_error,
                WebsocketsEventType.CLOSED: on_event.on_closed,
                WebsocketsEventType.INPUT_AUDIO_BUFFER_COMMITTED: on_event.on_input_audio_buffer_committed,
                WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_UPDATE: on_event.on_transcriptions_message_update,
                WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_COMPLETED: on_event.on_transcriptions_message_completed,
            }
        super().__init__(
            base_url=base_url,
            auth=auth,
            requester=requester,
            path="v1/audio/transcriptions",
            on_event=on_event,
            wait_events=[WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_COMPLETED],
            **kwargs,
        )

    async def update(self, data: TranscriptionsUpdateEvent.InputAudio) -> None:
        await self._input_queue.put(TranscriptionsUpdateEvent.model_validate({"data": data}))

    async def append(self, delta: bytes) -> None:
        await self._input_queue.put(
            InputAudioBufferAppendEvent.model_validate(
                {
                    "data": InputAudioBufferAppendEvent.Data.model_validate(
                        {
                            "delta": delta,
                        }
                    )
                }
            )
        )

    async def commit(self) -> None:
        await self._input_queue.put(InputAudioBufferCommitEvent.model_validate({}))

    def _load_event(self, message: Dict) -> Optional[WebsocketsEvent]:
        event_id = message.get("event_id") or ""
        event_type = message.get("type") or ""
        data = message.get("data") or {}
        if event_type == WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_COMPLETED.value:
            return TranscriptionsMessageCompletedEvent.model_validate(
                {
                    "event_id": event_id,
                }
            )
        elif event_type == WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_UPDATE.value:
            return TranscriptionsMessageUpdateEvent.model_validate(
                {
                    "event_id": event_id,
                    "data": TranscriptionsMessageUpdateEvent.Data.model_validate(
                        {
                            "content": data.get("content") or "",
                        }
                    ),
                }
            )
        elif event_type == WebsocketsEventType.INPUT_AUDIO_BUFFER_COMMITTED.value:
            pass
        else:
            log_warning("[v1/audio/transcriptions] unknown event=%s", event_type)
        return None


class AsyncWebsocketsAudioTranscriptionsClient:
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._auth = auth
        self._requester = requester

    def create(
        self,
        *,
        on_event: Union[AsyncWebsocketsAudioTranscriptionsEventHandler, Dict[WebsocketsEventType, Callable]],
        **kwargs,
    ) -> AsyncWebsocketsAudioTranscriptionsCreateClient:
        return AsyncWebsocketsAudioTranscriptionsCreateClient(
            base_url=self._base_url,
            auth=self._auth,
            requester=self._requester,
            on_event=on_event,
            **kwargs,
        )
