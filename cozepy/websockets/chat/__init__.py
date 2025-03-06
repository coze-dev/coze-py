from typing import Any, Callable, Dict, List, Optional, Union

from pydantic import BaseModel

from cozepy import Chat, Message, ToolOutput
from cozepy.log import log_warning
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


# req
class ChatUpdateEvent(WebsocketsEvent):
    class ChatConfig(BaseModel):
        conversation_id: Optional[str] = None
        user_id: Optional[str] = None
        meta_data: Optional[Dict[str, str]] = None
        custom_variables: Optional[Dict[str, str]] = None
        extra_params: Optional[Dict[str, str]] = None
        auto_save_history: Optional[bool] = None
        parameters: Optional[Dict[str, Any]] = None

    class Data(BaseModel):
        output_audio: Optional[OutputAudio] = None
        input_audio: Optional[InputAudio] = None
        chat_config: Optional["ChatUpdateEvent.ChatConfig"] = None

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


# resp
class ConversationChatRequiresActionEvent(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CHAT_REQUIRES_ACTION
    data: Chat


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
class ConversationChatCanceledEvent(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CHAT_CANCELED


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

    def on_conversation_chat_canceled(self, cli: "WebsocketsChatClient", event: ConversationChatCanceledEvent):
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
            on_event = on_event.to_dict(
                {
                    WebsocketsEventType.CHAT_CREATED: on_event.on_chat_created,
                    WebsocketsEventType.CHAT_UPDATED: on_event.on_chat_updated,
                    WebsocketsEventType.INPUT_AUDIO_BUFFER_COMPLETED: on_event.on_input_audio_buffer_completed,
                    WebsocketsEventType.CONVERSATION_CHAT_CREATED: on_event.on_conversation_chat_created,
                    WebsocketsEventType.CONVERSATION_CHAT_IN_PROGRESS: on_event.on_conversation_chat_in_progress,
                    WebsocketsEventType.CONVERSATION_MESSAGE_DELTA: on_event.on_conversation_message_delta,
                    WebsocketsEventType.CONVERSATION_AUDIO_TRANSCRIPT_COMPLETED: on_event.on_conversation_audio_transcript_completed,
                    WebsocketsEventType.CONVERSATION_CHAT_REQUIRES_ACTION: on_event.on_conversation_chat_requires_action,
                    WebsocketsEventType.CONVERSATION_MESSAGE_COMPLETED: on_event.on_conversation_message_completed,
                    WebsocketsEventType.CONVERSATION_AUDIO_DELTA: on_event.on_conversation_audio_delta,
                    WebsocketsEventType.CONVERSATION_AUDIO_COMPLETED: on_event.on_conversation_audio_completed,
                    WebsocketsEventType.CONVERSATION_CHAT_COMPLETED: on_event.on_conversation_chat_completed,
                    WebsocketsEventType.CONVERSATION_CHAT_CANCELED: on_event.on_conversation_chat_canceled,
                }
            )
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
            **kwargs,
        )

    def chat_update(self, data: ChatUpdateEvent.Data) -> None:
        self._input_queue.put(ChatUpdateEvent.model_validate({"data": data}))

    def conversation_chat_submit_tool_outputs(self, data: ConversationChatSubmitToolOutputsEvent.Data):
        self._input_queue.put(ConversationChatSubmitToolOutputsEvent.model_validate({"data": data}))

    def conversation_chat_cancel(self):
        self._input_queue.put(ConversationChatCancelEvent.model_validate({}))

    def input_audio_buffer_append(self, data: InputAudioBufferAppendEvent.Data) -> None:
        self._input_queue.put(InputAudioBufferAppendEvent.model_validate({"data": data}))

    def input_audio_buffer_complete(self) -> None:
        self._input_queue.put(InputAudioBufferCompleteEvent.model_validate({}))

    def _load_event(self, message: Dict) -> Optional[WebsocketsEvent]:
        event_id = message.get("id") or ""
        detail = WebsocketsEvent.Detail.model_validate(message.get("detail") or {})
        event_type = message.get("event_type") or ""
        data = message.get("data") or {}
        if event_type == WebsocketsEventType.CHAT_CREATED.value:
            return ChatCreatedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        elif event_type == WebsocketsEventType.CHAT_UPDATED.value:
            return ChatUpdatedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                    "data": ChatUpdateEvent.Data.model_validate(data),
                }
            )
        elif event_type == WebsocketsEventType.INPUT_AUDIO_BUFFER_COMPLETED.value:
            return InputAudioBufferCompletedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_CHAT_CREATED.value:
            return ConversationChatCreatedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                    "data": Chat.model_validate(data),
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_CHAT_IN_PROGRESS.value:
            return ConversationChatInProgressEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_MESSAGE_DELTA.value:
            return ConversationMessageDeltaEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                    "data": Message.model_validate(data),
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_AUDIO_TRANSCRIPT_COMPLETED.value:
            return ConversationAudioTranscriptCompletedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                    "data": ConversationAudioTranscriptCompletedEvent.Data.model_validate(data),
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_CHAT_REQUIRES_ACTION.value:
            return ConversationChatRequiresActionEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                    "data": Chat.model_validate(data),
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_MESSAGE_COMPLETED.value:
            return ConversationMessageCompletedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_AUDIO_DELTA.value:
            return ConversationAudioDeltaEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                    "data": Message.model_validate(data),
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_AUDIO_COMPLETED.value:
            return ConversationAudioCompletedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_CHAT_COMPLETED.value:
            return ConversationChatCompletedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                    "data": Chat.model_validate(data),
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_CHAT_CANCELED.value:
            return ConversationChatCanceledEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        else:
            log_warning("[%s] unknown event, type=%s, logid=%s", self._path, event_type, detail.logid)
        return None


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

    async def on_conversation_chat_canceled(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationChatCanceledEvent
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
            on_event = on_event.to_dict(
                {
                    WebsocketsEventType.CHAT_CREATED: on_event.on_chat_created,
                    WebsocketsEventType.CHAT_UPDATED: on_event.on_chat_updated,
                    WebsocketsEventType.INPUT_AUDIO_BUFFER_COMPLETED: on_event.on_input_audio_buffer_completed,
                    WebsocketsEventType.CONVERSATION_CHAT_CREATED: on_event.on_conversation_chat_created,
                    WebsocketsEventType.CONVERSATION_CHAT_IN_PROGRESS: on_event.on_conversation_chat_in_progress,
                    WebsocketsEventType.CONVERSATION_MESSAGE_DELTA: on_event.on_conversation_message_delta,
                    WebsocketsEventType.CONVERSATION_AUDIO_TRANSCRIPT_COMPLETED: on_event.on_conversation_audio_transcript_completed,
                    WebsocketsEventType.CONVERSATION_CHAT_REQUIRES_ACTION: on_event.on_conversation_chat_requires_action,
                    WebsocketsEventType.CONVERSATION_MESSAGE_COMPLETED: on_event.on_conversation_message_completed,
                    WebsocketsEventType.CONVERSATION_AUDIO_DELTA: on_event.on_conversation_audio_delta,
                    WebsocketsEventType.CONVERSATION_AUDIO_COMPLETED: on_event.on_conversation_audio_completed,
                    WebsocketsEventType.CONVERSATION_CHAT_COMPLETED: on_event.on_conversation_chat_completed,
                    WebsocketsEventType.CONVERSATION_CHAT_CANCELED: on_event.on_conversation_chat_canceled,
                }
            )
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
            **kwargs,
        )

    async def chat_update(self, data: ChatUpdateEvent.Data) -> None:
        await self._input_queue.put(ChatUpdateEvent.model_validate({"data": data}))

    async def conversation_chat_submit_tool_outputs(self, data: ConversationChatSubmitToolOutputsEvent.Data) -> None:
        await self._input_queue.put(ConversationChatSubmitToolOutputsEvent.model_validate({"data": data}))

    async def conversation_chat_cancel(self) -> None:
        await self._input_queue.put(ConversationChatCancelEvent.model_validate({}))

    async def input_audio_buffer_append(self, data: InputAudioBufferAppendEvent.Data) -> None:
        await self._input_queue.put(InputAudioBufferAppendEvent.model_validate({"data": data}))

    async def input_audio_buffer_complete(self) -> None:
        await self._input_queue.put(InputAudioBufferCompleteEvent.model_validate({}))

    def _load_event(self, message: Dict) -> Optional[WebsocketsEvent]:
        event_id = message.get("id") or ""
        detail = WebsocketsEvent.Detail.model_validate(message.get("detail") or {})
        event_type = message.get("event_type") or ""
        data = message.get("data") or {}
        if event_type == WebsocketsEventType.CHAT_CREATED.value:
            return ChatCreatedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        elif event_type == WebsocketsEventType.CHAT_UPDATED.value:
            return ChatUpdatedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                    "data": ChatUpdateEvent.Data.model_validate(data),
                }
            )
        elif event_type == WebsocketsEventType.INPUT_AUDIO_BUFFER_COMPLETED.value:
            return InputAudioBufferCompletedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_CHAT_CREATED.value:
            return ConversationChatCreatedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                    "data": Chat.model_validate(data),
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_CHAT_IN_PROGRESS.value:
            return ConversationChatInProgressEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_MESSAGE_DELTA.value:
            return ConversationMessageDeltaEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                    "data": Message.model_validate(data),
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_AUDIO_TRANSCRIPT_COMPLETED.value:
            return ConversationAudioTranscriptCompletedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                    "data": ConversationAudioTranscriptCompletedEvent.Data.model_validate(data),
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_CHAT_REQUIRES_ACTION.value:
            return ConversationChatRequiresActionEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                    "data": Chat.model_validate(data),
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_MESSAGE_COMPLETED.value:
            return ConversationMessageCompletedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_AUDIO_DELTA.value:
            return ConversationAudioDeltaEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                    "data": Message.model_validate(data),
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_AUDIO_COMPLETED.value:
            return ConversationAudioCompletedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_CHAT_COMPLETED.value:
            return ConversationChatCompletedEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                    "data": Chat.model_validate(data),
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_CHAT_CANCELED.value:
            return ConversationChatCanceledEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                }
            )
        else:
            log_warning("[%s] unknown event, type=%s, logid=%s", self._path, event_type, detail.logid)
        return None


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
