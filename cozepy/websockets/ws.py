import abc
import asyncio
import json
from abc import ABC
from contextlib import asynccontextmanager
from enum import Enum
from typing import Callable, Dict, List, Optional

import websockets
from websockets import InvalidStatus
from websockets.asyncio.connection import Connection

from cozepy import Auth, CozeAPIError
from cozepy.log import log_debug, log_info
from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash
from cozepy.version import coze_client_user_agent, user_agent


class WebsocketsEventType(str, Enum):
    # common
    ERROR = "error"
    CLOSED = "closed"

    # v1/audio/speech
    # req
    INPUT_TEXT_BUFFER_APPEND = "input_text_buffer.append"
    INPUT_TEXT_BUFFER_COMMIT = "input_text_buffer.commit"
    SPEECH_UPDATE = "speech.update"
    # resp
    # v1/audio/speech
    INPUT_TEXT_BUFFER_COMMITTED = "input_text_buffer.committed"  # ignored
    SPEECH_AUDIO_UPDATE = "speech.audio.update"
    SPEECH_AUDIO_COMPLETED = "speech.audio.completed"

    # v1/audio/transcriptions
    # req
    INPUT_AUDIO_BUFFER_APPEND = "input_audio_buffer.append"
    INPUT_AUDIO_BUFFER_COMMIT = "input_audio_buffer.commit"
    TRANSCRIPTIONS_UPDATE = "transcriptions.update"
    # resp
    INPUT_AUDIO_BUFFER_COMMITTED = "input_audio_buffer.committed"  # ignored
    TRANSCRIPTIONS_MESSAGE_UPDATE = "transcriptions.message.update"
    TRANSCRIPTIONS_MESSAGE_COMPLETED = "transcriptions.message.completed"

    # v1/chat
    # req
    # INPUT_AUDIO_BUFFER_APPEND = "input_audio_buffer.append"
    # INPUT_AUDIO_BUFFER_COMMIT = "input_audio_buffer.commit"
    CHAT_UPDATE = "chat.update"
    # resp
    CONVERSATION_CHAT_CREATED = "conversation.chat.created"
    CONVERSATION_MESSAGE_DELTA = "conversation.message.delta"
    CONVERSATION_CHAT_REQUIRES_ACTION = "conversation.chat.requires_action"
    CONVERSATION_AUDIO_DELTA = "conversation.audio.delta"
    CONVERSATION_CHAT_COMPLETED = "conversation.chat.completed"


class WebsocketsEvent(CozeModel, ABC):
    event_id: Optional[str] = None
    type: WebsocketsEventType


class AsyncWebsocketsBaseClient(abc.ABC):
    def __init__(
        self,
        base_url: str,
        auth: Auth,
        requester: Requester,
        path: str,
        query: Optional[Dict[str, str]] = None,
        on_event: Optional[Dict[WebsocketsEventType, Callable]] = None,
        wait_events: Optional[List[WebsocketsEventType]] = None,
        **kwargs,
    ):
        self._base_url = remove_url_trailing_slash(base_url)
        self._auth = auth
        self._requester = requester
        self._path = path
        self._ws_url = self._base_url + "/" + path
        if query:
            self._ws_url += "?" + "&".join([f"{k}={v}" for k, v in query.items()])
        self._on_event = on_event.copy() if on_event else {}
        self._headers = kwargs.get("headers")
        self._wait_events = wait_events.copy() if wait_events else []

        self._input_queue: asyncio.Queue[Optional[WebsocketsEvent]] = asyncio.Queue()
        self._ws: Optional[Connection] = None
        self._send_task: Optional[asyncio.Task] = None
        self._receive_task: Optional[asyncio.Task] = None

    @asynccontextmanager
    async def __call__(self):
        try:
            await self.connect()
            yield self
        finally:
            await self.close()

    async def connect(self):
        headers = {
            "Authorization": f"Bearer {self._auth.token}",
            "X-Coze-Client-User-Agent": coze_client_user_agent(),
            **(self._headers or {}),
        }
        try:
            self._ws = await websockets.connect(
                self._ws_url,
                user_agent_header=user_agent(),
                additional_headers=headers,
            )
            log_info("[%s] connected to websocket", self._path)

            self._receive_task = asyncio.create_task(self._receive_loop())
            self._send_task = asyncio.create_task(self._send_loop())
        except InvalidStatus as e:
            raise CozeAPIError(None, f"{e}", e.response.headers.get("x-tt-logid")) from e

    async def wait(self, events: Optional[List[WebsocketsEventType]] = None, wait_all=True) -> None:
        if events is None:
            events = self._wait_events
        await self._wait_completed(events, wait_all=wait_all)

    def on(self, event_type: WebsocketsEventType, handler: Callable):
        self._on_event[event_type] = handler

    async def close(self) -> None:
        await self._close()

    async def _send_loop(self) -> None:
        try:
            while True:
                if event := await self._input_queue.get():
                    await self._send_event(event)
                self._input_queue.task_done()
        except Exception as e:
            await self._handle_error(e)

    async def _receive_loop(self) -> None:
        try:
            while True:
                if not self._ws:
                    log_debug("[%s] empty websocket conn, close", self._path)
                    break

                data = await self._ws.recv()
                message = json.loads(data)
                event_type = message.get("type")
                log_debug("[%s] receive event, type=%s, event=%s", self._path, event_type, data)

                if handler := self._on_event.get(event_type):
                    if event := self._load_event(message):
                        await handler(self, event)
        except Exception as e:
            await self._handle_error(e)

    @abc.abstractmethod
    def _load_event(self, message: Dict) -> Optional[WebsocketsEvent]: ...

    async def _wait_completed(self, events: List[WebsocketsEventType], wait_all: bool) -> None:
        future: asyncio.Future[None] = asyncio.Future()
        original_handlers = {}
        completed_events = set()

        async def _handle_completed(client, event):
            event_type = event.type
            completed_events.add(event_type)

            if wait_all:
                # 所有事件都需要完成
                if completed_events == set(events):
                    future.set_result(None)
            else:
                # 任意一个事件完成即可
                future.set_result(None)

        # 为每个指定的事件类型临时注册处理函数
        for event_type in events:
            original_handlers[event_type] = self._on_event.get(event_type)
            self._on_event[event_type] = _handle_completed

        try:
            # 等待直到满足完成条件
            await future
        finally:
            # 恢复所有原来的处理函数
            for event_type, handler in original_handlers.items():
                if handler:
                    self._on_event[event_type] = handler
                else:
                    self._on_event.pop(event_type, None)

    async def _handle_error(self, error: Exception) -> None:
        if handler := self._on_event.get(WebsocketsEventType.ERROR):
            await handler(self, error)
        else:
            raise error

    async def _close(self) -> None:
        log_info("[%s] connect closed", self._path)
        if self._send_task:
            self._send_task.cancel()
        if self._receive_task:
            self._receive_task.cancel()

        if self._ws:
            await self._ws.close()
            self._ws = None

        while not self._input_queue.empty():
            await self._input_queue.get()

        if handler := self._on_event.get(WebsocketsEventType.CLOSED):
            await handler(self)

    async def _send_event(self, event: WebsocketsEvent) -> None:
        log_debug("[%s] send event, type=%s", self._path, event.type.value)
        if self._ws:
            await self._ws.send(event.model_dump_json(), True)


class AsyncWebsocketsBaseEventHandler(object):
    async def on_error(self, cli: "AsyncWebsocketsBaseClient", e: Exception):
        pass

    async def on_closed(self, cli: "AsyncWebsocketsBaseClient"):
        pass
