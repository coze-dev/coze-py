from typing import Callable, Dict, Optional, Union

from cozepy import Chat, Message
from cozepy.auth import Auth
from cozepy.log import log_warning
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash
from cozepy.websockets.audio.transcriptions import InputAudioBufferAppendEvent, InputAudioBufferCommitEvent
from cozepy.websockets.ws import (
    AsyncWebsocketsBaseClient,
    AsyncWebsocketsBaseEventHandler,
    WebsocketsEvent,
    WebsocketsEventType,
)


# resp
class ConversationChatCreatedEvent(WebsocketsEvent):
    type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CHAT_CREATED
    data: Chat


# resp
class ConversationMessageDeltaEvent(WebsocketsEvent):
    type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_MESSAGE_DELTA
    data: Message


# resp
class ConversationAudioDeltaEvent(WebsocketsEvent):
    type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_AUDIO_DELTA
    data: Message


# resp
class ConversationChatCompletedEvent(WebsocketsEvent):
    type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CHAT_COMPLETED
    data: Chat


class AsyncWebsocketsChatEventHandler(AsyncWebsocketsBaseEventHandler):
    def on_conversation_chat_created(self, cli: "AsyncWebsocketsChatCreateClient", event: ConversationChatCreatedEvent):
        pass

    def on_conversation_message_delta(
        self, cli: "AsyncWebsocketsChatCreateClient", event: ConversationMessageDeltaEvent
    ):
        pass

    # def on_conversation_chat_requires_action(self, cli: 'AsyncWebsocketsChatCreateClient',
    #                                          event: ConversationChatRequiresActionEvent):
    #     pass

    def on_conversation_audio_delta(self, cli: "AsyncWebsocketsChatCreateClient", event: ConversationAudioDeltaEvent):
        pass

    def on_conversation_chat_completed(
        self, cli: "AsyncWebsocketsChatCreateClient", event: ConversationChatCompletedEvent
    ):
        pass


class AsyncWebsocketsChatCreateClient(AsyncWebsocketsBaseClient):
    def __init__(
        self,
        base_url: str,
        auth: Auth,
        requester: Requester,
        bot_id: str,
        on_event: Union[AsyncWebsocketsChatEventHandler, Dict[WebsocketsEventType, Callable]],
        **kwargs,
    ):
        if isinstance(on_event, AsyncWebsocketsChatEventHandler):
            on_event = {
                WebsocketsEventType.ERROR: on_event.on_error,
                WebsocketsEventType.CLOSED: on_event.on_closed,
                WebsocketsEventType.CONVERSATION_CHAT_CREATED: on_event.on_conversation_chat_created,
                WebsocketsEventType.CONVERSATION_MESSAGE_DELTA: on_event.on_conversation_message_delta,
                # EventType.CONVERSATION_CHAT_REQUIRES_ACTION: on_event.on_conversation_chat_requires_action,
                WebsocketsEventType.CONVERSATION_AUDIO_DELTA: on_event.on_conversation_audio_delta,
                WebsocketsEventType.CONVERSATION_CHAT_COMPLETED: on_event.on_conversation_chat_completed,
            }
        super().__init__(
            base_url=base_url,
            auth=auth,
            requester=requester,
            path="v1/chat",
            query={
                "bot_id": bot_id,
            },
            on_event=on_event,
            wait_events=[WebsocketsEventType.CONVERSATION_CHAT_COMPLETED],
            **kwargs,
        )

    # async def update(self, event: TranscriptionsUpdateEventInputAudio) -> None:
    #     await self._input_queue.put(TranscriptionsUpdateEvent.load(event))

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
        if event_type == WebsocketsEventType.CONVERSATION_CHAT_CREATED.value:
            return ConversationChatCreatedEvent.model_validate(
                {
                    "data": Chat.model_validate(data),
                    "event_id": event_id,
                }
            )
        if event_type == WebsocketsEventType.CONVERSATION_MESSAGE_DELTA.value:
            return ConversationMessageDeltaEvent.model_validate(
                {
                    "data": Message.model_validate(data),
                    "event_id": event_id,
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_AUDIO_DELTA.value:
            return ConversationAudioDeltaEvent.model_validate(
                {
                    "data": Message.model_validate(data),
                    "event_id": event_id,
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_CHAT_COMPLETED.value:
            return ConversationChatCompletedEvent.model_validate(
                {
                    "data": Chat.model_validate(data),
                    "event_id": event_id,
                }
            )
        else:
            log_warning("[%s] unknown event=%s", self._path, event_type)
        return None


class AsyncWebsocketsChatClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._auth = auth
        self._requester = requester

    def create(
        self,
        *,
        bot_id: str,
        on_event: Union[AsyncWebsocketsChatEventHandler, Dict[WebsocketsEventType, Callable]],
        **kwargs,
    ) -> AsyncWebsocketsChatCreateClient:
        return AsyncWebsocketsChatCreateClient(
            base_url=self._base_url,
            auth=self._auth,
            requester=self._requester,
            bot_id=bot_id,
            on_event=on_event,
            **kwargs,
        )
