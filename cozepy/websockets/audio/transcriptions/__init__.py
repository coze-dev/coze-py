import base64
from typing import Callable, Dict, Optional, Union

from pydantic import BaseModel, field_serializer

from cozepy.log import log_warning
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash
from cozepy.websockets.ws import (
    AsyncWebsocketsBaseClient,
    AsyncWebsocketsBaseEventHandler,
    InputAudio,
    WebsocketsBaseClient,
    WebsocketsBaseEventHandler,
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

    event_type: WebsocketsEventType = WebsocketsEventType.INPUT_AUDIO_BUFFER_APPEND
    data: Data

    def _dump_without_delta(self):
        return {
            "id": self.id,
            "type": self.event_type.value,
            "detail": self.detail,
            "data": {
                "delta_length": len(self.data.delta) if self.data and self.data.delta else 0,
            },
        }


# req
class InputAudioBufferCompleteEvent(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.INPUT_AUDIO_BUFFER_COMPLETE


# req
class TranscriptionsUpdateEvent(WebsocketsEvent):
    class Data(BaseModel):
        input_audio: Optional[InputAudio] = None

    event_type: WebsocketsEventType = WebsocketsEventType.TRANSCRIPTIONS_UPDATE
    data: Data


# resp
class TranscriptionsCreatedEvent(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.TRANSCRIPTIONS_CREATED


# resp
class InputAudioBufferCompletedEvent(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.INPUT_AUDIO_BUFFER_COMPLETED


# resp
class TranscriptionsMessageUpdateEvent(WebsocketsEvent):
    class Data(BaseModel):
        content: str

    event_type: WebsocketsEventType = WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_UPDATE
    data: Data


# resp
class TranscriptionsMessageCompletedEvent(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_COMPLETED


class WebsocketsAudioTranscriptionsEventHandler(WebsocketsBaseEventHandler):
    def on_transcriptions_created(self, cli: "WebsocketsAudioTranscriptionsClient", event: TranscriptionsCreatedEvent):
        pass

    def on_input_audio_buffer_completed(
        self, cli: "WebsocketsAudioTranscriptionsClient", event: InputAudioBufferCompletedEvent
    ):
        pass

    def on_transcriptions_message_update(
        self, cli: "WebsocketsAudioTranscriptionsClient", event: TranscriptionsMessageUpdateEvent
    ):
        pass

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
            on_event = on_event.to_dict(
                {
                    WebsocketsEventType.TRANSCRIPTIONS_CREATED: on_event.on_transcriptions_created,
                    WebsocketsEventType.INPUT_AUDIO_BUFFER_COMPLETED: on_event.on_input_audio_buffer_completed,
                    WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_UPDATE: on_event.on_transcriptions_message_update,
                    WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_COMPLETED: on_event.on_transcriptions_message_completed,
                }
            )
        super().__init__(
            base_url=base_url,
            requester=requester,
            path="v1/audio/transcriptions",
            on_event=on_event,  # type: ignore
            wait_events=[WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_COMPLETED],
            **kwargs,
        )

    def transcriptions_update(self, data: TranscriptionsUpdateEvent.Data) -> None:
        self._input_queue.put(TranscriptionsUpdateEvent.model_validate({"data": data}))

    def input_audio_buffer_append(self, data: InputAudioBufferAppendEvent.Data) -> None:
        self._input_queue.put(InputAudioBufferAppendEvent.model_validate({"data": data}))

    def input_audio_buffer_complete(self) -> None:
        self._input_queue.put(InputAudioBufferCompleteEvent.model_validate({}))

    def _load_event(self, message: Dict) -> Optional[WebsocketsEvent]:
        event_id = message.get("id") or ""
        event_type = message.get("event_type") or ""
        detail = WebsocketsEvent.Detail.model_validate(message.get("detail") or {})
        data = message.get("data") or {}
        if event_type == WebsocketsEventType.TRANSCRIPTIONS_CREATED.value:
            return TranscriptionsCreatedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        elif event_type == WebsocketsEventType.INPUT_AUDIO_BUFFER_COMPLETED.value:
            return InputAudioBufferCompletedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        elif event_type == WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_UPDATE.value:
            return TranscriptionsMessageUpdateEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                    "data": TranscriptionsMessageUpdateEvent.Data.model_validate(
                        {
                            "content": data.get("content") or "",
                        }
                    ),
                }
            )
        elif event_type == WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_COMPLETED.value:
            return TranscriptionsMessageCompletedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        else:
            log_warning("[v1/audio/transcriptions] unknown event=%s, logid=%s", event_type, detail.logid)
        return None


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
    async def on_transcriptions_created(
        self, cli: "AsyncWebsocketsAudioTranscriptionsClient", event: TranscriptionsCreatedEvent
    ):
        pass

    async def on_input_audio_buffer_completed(
        self, cli: "AsyncWebsocketsAudioTranscriptionsClient", event: InputAudioBufferCompletedEvent
    ):
        pass

    async def on_transcriptions_message_update(
        self, cli: "AsyncWebsocketsAudioTranscriptionsClient", event: TranscriptionsMessageUpdateEvent
    ):
        pass

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
            on_event = on_event.to_dict(
                {
                    WebsocketsEventType.TRANSCRIPTIONS_CREATED: on_event.on_transcriptions_created,
                    WebsocketsEventType.INPUT_AUDIO_BUFFER_COMPLETED: on_event.on_input_audio_buffer_completed,
                    WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_UPDATE: on_event.on_transcriptions_message_update,
                    WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_COMPLETED: on_event.on_transcriptions_message_completed,
                }
            )
        super().__init__(
            base_url=base_url,
            requester=requester,
            path="v1/audio/transcriptions",
            on_event=on_event,  # type: ignore
            wait_events=[WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_COMPLETED],
            **kwargs,
        )

    async def transcriptions_update(self, data: InputAudio) -> None:
        await self._input_queue.put(TranscriptionsUpdateEvent.model_validate({"data": data}))

    async def input_audio_buffer_append(self, data: InputAudioBufferAppendEvent.Data) -> None:
        await self._input_queue.put(InputAudioBufferAppendEvent.model_validate({"data": data}))

    async def input_audio_buffer_complete(self) -> None:
        await self._input_queue.put(InputAudioBufferCompleteEvent.model_validate({}))

    def _load_event(self, message: Dict) -> Optional[WebsocketsEvent]:
        event_id = message.get("id") or ""
        event_type = message.get("event_type") or ""
        detail = WebsocketsEvent.Detail.model_validate(message.get("detail") or {})
        data = message.get("data") or {}
        if event_type == WebsocketsEventType.TRANSCRIPTIONS_CREATED.value:
            return TranscriptionsCreatedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        elif event_type == WebsocketsEventType.INPUT_AUDIO_BUFFER_COMPLETED.value:
            return InputAudioBufferCompletedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        elif event_type == WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_UPDATE.value:
            return TranscriptionsMessageUpdateEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                    "data": TranscriptionsMessageUpdateEvent.Data.model_validate(
                        {
                            "content": data.get("content") or "",
                        }
                    ),
                }
            )
        elif event_type == WebsocketsEventType.TRANSCRIPTIONS_MESSAGE_COMPLETED.value:
            return TranscriptionsMessageCompletedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        else:
            log_warning("[v1/audio/transcriptions] unknown event=%s, logid=%s", event_type, detail.logid)
        return None


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
