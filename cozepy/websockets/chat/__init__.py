from typing import Callable, Dict, Optional, Union

from cozepy import Chat, Message
from cozepy.auth import Auth
from cozepy.log import log_warning
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash
from cozepy.websockets.audio.transcriptions import (
    InputAudioBufferAppendEvent,
    InputAudioBufferCompletedEvent,
    InputAudioBufferCompleteEvent,
)
from cozepy.websockets.ws import (
    AsyncWebsocketsBaseClient,
    AsyncWebsocketsBaseEventHandler,
    WebsocketsBaseClient,
    WebsocketsBaseEventHandler,
    WebsocketsEvent,
    WebsocketsEventType,
)


# req todo
class ChatUpdateEvent(WebsocketsEvent):
    type: WebsocketsEventType = WebsocketsEventType.CHAT_UPDATE


# resp
class ConversationChatCreatedEvent(WebsocketsEvent):
    type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CHAT_CREATED
    data: Chat


# resp
class ConversationMessageDeltaEvent(WebsocketsEvent):
    type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_MESSAGE_DELTA
    data: Message


# resp todo
class ConversationChatRequiresActionEvent(WebsocketsEvent):
    type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CHAT_REQUIRES_ACTION


# resp
class ConversationAudioDeltaEvent(WebsocketsEvent):
    type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_AUDIO_DELTA
    data: Message


# resp
class ConversationChatCompletedEvent(WebsocketsEvent):
    type: WebsocketsEventType = WebsocketsEventType.CONVERSATION_CHAT_COMPLETED
    data: Chat


class WebsocketsChatEventHandler(WebsocketsBaseEventHandler):
    def on_input_audio_buffer_completed(self, cli: "WebsocketsChatClient", event: InputAudioBufferCompletedEvent):
        pass

    def on_conversation_chat_created(self, cli: "WebsocketsChatClient", event: ConversationChatCreatedEvent):
        pass

    def on_conversation_message_delta(self, cli: "WebsocketsChatClient", event: ConversationMessageDeltaEvent):
        pass

    def on_conversation_chat_requires_action(
        self, cli: "WebsocketsChatClient", event: ConversationChatRequiresActionEvent
    ):
        pass

    def on_conversation_audio_delta(self, cli: "WebsocketsChatClient", event: ConversationAudioDeltaEvent):
        pass

    def on_conversation_chat_completed(self, cli: "WebsocketsChatClient", event: ConversationChatCompletedEvent):
        pass


class WebsocketsChatClient(WebsocketsBaseClient):
    def __init__(
        self,
        base_url: str,
        auth: Auth,
        requester: Requester,
        bot_id: str,
        on_event: Union[WebsocketsChatEventHandler, Dict[WebsocketsEventType, Callable]],
        **kwargs,
    ):
        if isinstance(on_event, WebsocketsChatEventHandler):
            on_event = on_event.to_dict(
                {
                    WebsocketsEventType.INPUT_AUDIO_BUFFER_COMPLETED: on_event.on_input_audio_buffer_completed,
                    WebsocketsEventType.CONVERSATION_CHAT_CREATED: on_event.on_conversation_chat_created,
                    WebsocketsEventType.CONVERSATION_MESSAGE_DELTA: on_event.on_conversation_message_delta,
                    WebsocketsEventType.CONVERSATION_CHAT_REQUIRES_ACTION: on_event.on_conversation_chat_requires_action,
                    WebsocketsEventType.CONVERSATION_AUDIO_DELTA: on_event.on_conversation_audio_delta,
                    WebsocketsEventType.CONVERSATION_CHAT_COMPLETED: on_event.on_conversation_chat_completed,
                }
            )
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

    def input_audio_buffer_append(self, data: InputAudioBufferAppendEvent) -> None:
        self._input_queue.put(InputAudioBufferAppendEvent.model_validate({"data": data}))

    def input_audio_buffer_complete(self) -> None:
        self._input_queue.put(InputAudioBufferCompleteEvent.model_validate({}))

    def _load_event(self, message: Dict) -> Optional[WebsocketsEvent]:
        event_id = message.get("event_id") or ""
        logid = message.get("logid") or ""
        event_type = message.get("type") or ""
        data = message.get("data") or {}
        if event_type == WebsocketsEventType.INPUT_AUDIO_BUFFER_COMPLETED.value:
            return InputAudioBufferCompletedEvent.model_validate(
                {
                    "event_id": event_id,
                    "logid": logid,
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_CHAT_CREATED.value:
            return ConversationChatCreatedEvent.model_validate(
                {
                    "event_id": event_id,
                    "logid": logid,
                    "data": Chat.model_validate(data),
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_MESSAGE_DELTA.value:
            return ConversationMessageDeltaEvent.model_validate(
                {
                    "event_id": event_id,
                    "logid": logid,
                    "data": Message.model_validate(data),
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_CHAT_REQUIRES_ACTION.value:
            return ConversationChatRequiresActionEvent.model_validate(
                {
                    "event_id": event_id,
                    "logid": logid,
                    "data": Message.model_validate(data),  # todo
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_AUDIO_DELTA.value:
            return ConversationAudioDeltaEvent.model_validate(
                {
                    "event_id": event_id,
                    "logid": logid,
                    "data": Message.model_validate(data),
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_CHAT_COMPLETED.value:
            return ConversationChatCompletedEvent.model_validate(
                {
                    "event_id": event_id,
                    "logid": logid,
                    "data": Chat.model_validate(data),
                }
            )
        else:
            log_warning("[%s] unknown event, type=%s, logid=%s", self._path, event_type, logid)
        return None


class WebsocketsChatBuildClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._auth = auth
        self._requester = requester

    def create(
        self,
        *,
        bot_id: str,
        on_event: Union[WebsocketsChatEventHandler, Dict[WebsocketsEventType, Callable]],
        **kwargs,
    ) -> WebsocketsChatClient:
        return WebsocketsChatClient(
            base_url=self._base_url,
            auth=self._auth,
            requester=self._requester,
            bot_id=bot_id,
            on_event=on_event,
            **kwargs,
        )


class AsyncWebsocketsChatEventHandler(AsyncWebsocketsBaseEventHandler):
    async def on_input_audio_buffer_completed(
        self, cli: "AsyncWebsocketsChatClient", event: InputAudioBufferCompletedEvent
    ):
        pass

    async def on_conversation_chat_created(self, cli: "AsyncWebsocketsChatClient", event: ConversationChatCreatedEvent):
        pass

    async def on_conversation_message_delta(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationMessageDeltaEvent
    ):
        pass

    async def on_conversation_chat_requires_action(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationChatRequiresActionEvent
    ):
        pass

    async def on_conversation_audio_delta(self, cli: "AsyncWebsocketsChatClient", event: ConversationAudioDeltaEvent):
        pass

    async def on_conversation_chat_completed(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationChatCompletedEvent
    ):
        pass


class AsyncWebsocketsChatClient(AsyncWebsocketsBaseClient):
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
            on_event = on_event.to_dict(
                {
                    WebsocketsEventType.INPUT_AUDIO_BUFFER_COMPLETED: on_event.on_input_audio_buffer_completed,
                    WebsocketsEventType.CONVERSATION_CHAT_CREATED: on_event.on_conversation_chat_created,
                    WebsocketsEventType.CONVERSATION_MESSAGE_DELTA: on_event.on_conversation_message_delta,
                    WebsocketsEventType.CONVERSATION_CHAT_REQUIRES_ACTION: on_event.on_conversation_chat_requires_action,
                    WebsocketsEventType.CONVERSATION_AUDIO_DELTA: on_event.on_conversation_audio_delta,
                    WebsocketsEventType.CONVERSATION_CHAT_COMPLETED: on_event.on_conversation_chat_completed,
                }
            )
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

    async def chat_update(self, event: ChatUpdateEvent) -> None:
        # TODO
        await self._input_queue.put(event)

    async def input_audio_buffer_append(self, data: InputAudioBufferAppendEvent.Data) -> None:
        await self._input_queue.put(InputAudioBufferAppendEvent.model_validate({"data": data}))

    async def input_audio_buffer_complete(self) -> None:
        await self._input_queue.put(InputAudioBufferCompleteEvent.model_validate({}))

    def _load_event(self, message: Dict) -> Optional[WebsocketsEvent]:
        event_id = message.get("event_id") or ""
        logid = message.get("logid") or ""
        event_type = message.get("type") or ""
        data = message.get("data") or {}
        if event_type == WebsocketsEventType.INPUT_AUDIO_BUFFER_COMPLETED.value:
            return InputAudioBufferCompletedEvent.model_validate(
                {
                    "event_id": event_id,
                    "logid": logid,
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_CHAT_CREATED.value:
            return ConversationChatCreatedEvent.model_validate(
                {
                    "event_id": event_id,
                    "logid": logid,
                    "data": Chat.model_validate(data),
                }
            )
        if event_type == WebsocketsEventType.CONVERSATION_MESSAGE_DELTA.value:
            return ConversationMessageDeltaEvent.model_validate(
                {
                    "event_id": event_id,
                    "logid": logid,
                    "data": Message.model_validate(data),
                }
            )
        if event_type == WebsocketsEventType.CONVERSATION_CHAT_REQUIRES_ACTION.value:
            return ConversationChatRequiresActionEvent.model_validate(
                {
                    # TODO
                    "event_id": event_id,
                    "logid": logid,
                    "data": Message.model_validate(data),
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_AUDIO_DELTA.value:
            return ConversationAudioDeltaEvent.model_validate(
                {
                    "event_id": event_id,
                    "logid": logid,
                    "data": Message.model_validate(data),
                }
            )
        elif event_type == WebsocketsEventType.CONVERSATION_CHAT_COMPLETED.value:
            return ConversationChatCompletedEvent.model_validate(
                {
                    "event_id": event_id,
                    "logid": logid,
                    "data": Chat.model_validate(data),
                }
            )
        else:
            log_warning("[%s] unknown event, type=%s, logid=%s", self._path, event_type, logid)
        return None


class AsyncWebsocketsChatBuildClient(object):
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
    ) -> AsyncWebsocketsChatClient:
        return AsyncWebsocketsChatClient(
            base_url=self._base_url,
            auth=self._auth,
            requester=self._requester,
            bot_id=bot_id,
            on_event=on_event,
            **kwargs,
        )
