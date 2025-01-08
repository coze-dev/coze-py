import abc
import asyncio
import json
import queue
import threading
import traceback
from abc import ABC
from contextlib import asynccontextmanager, contextmanager
from enum import Enum
from typing import Callable, Dict, List, Optional

import websockets.asyncio.client
import websockets.sync.client
from websockets import InvalidStatus

from cozepy import Auth, CozeAPIError
from cozepy.log import log_debug, log_error, log_info
from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash
from cozepy.version import coze_client_user_agent, user_agent


class WebsocketsEventType(str, Enum):
    # common
    CLIENT_ERROR = "client_error"  # sdk error
    CLOSED = "closed"  # connection closed

    # error
    ERROR = "error"  # received error event

    # v1/audio/speech
    # req
    INPUT_TEXT_BUFFER_APPEND = "input_text_buffer.append"  # send text to server
    INPUT_TEXT_BUFFER_COMPLETE = (
        "input_text_buffer.complete"  # no text to send, after audio all received, can close connection
    )
    SPEECH_UPDATE = "speech.update"  # send speech config to server
    # resp
    # v1/audio/speech
    INPUT_TEXT_BUFFER_COMPLETED = "input_text_buffer.completed"  # received `input_text_buffer.complete` event
    SPEECH_AUDIO_UPDATE = "speech.audio.update"  # received `speech.update` event
    SPEECH_AUDIO_COMPLETED = "speech.audio.completed"  # all audio received, can close connection

    # v1/audio/transcriptions
    # req
    INPUT_AUDIO_BUFFER_APPEND = "input_audio_buffer.append"  # send audio to server
    INPUT_AUDIO_BUFFER_COMPLETE = (
        "input_audio_buffer.complete"  # no audio to send, after text all received, can close connection
    )
    TRANSCRIPTIONS_UPDATE = "transcriptions.update"  # send transcriptions config to server
    # resp
    INPUT_AUDIO_BUFFER_COMPLETED = "input_audio_buffer.completed"  # received `input_audio_buffer.complete` event
    TRANSCRIPTIONS_MESSAGE_UPDATE = "transcriptions.message.update"  # received `transcriptions.update` event
    TRANSCRIPTIONS_MESSAGE_COMPLETED = "transcriptions.message.completed"  # all audio received, can close connection

    # v1/chat
    # req
    # INPUT_AUDIO_BUFFER_APPEND = "input_audio_buffer.append" # send audio to server
    # INPUT_AUDIO_BUFFER_COMPLETE = "input_audio_buffer.complete" # no audio send, start chat
    CHAT_UPDATE = "chat.update"  # send chat config to server
    # resp
    # INPUT_AUDIO_BUFFER_COMPLETED = "input_audio_buffer.completed" # received `input_audio_buffer.complete` event
    CONVERSATION_CHAT_CREATED = "conversation.chat.created"  # audio ast completed, chat started
    CONVERSATION_MESSAGE_DELTA = "conversation.message.delta"  # get agent text message update
    CONVERSATION_CHAT_REQUIRES_ACTION = "conversation.chat.requires_action"  # need plugin submit
    CONVERSATION_AUDIO_DELTA = "conversation.audio.delta"  # get agent audio message update
    CONVERSATION_CHAT_COMPLETED = "conversation.chat.completed"  # all message received, can close connection


class WebsocketsEvent(CozeModel, ABC):
    type: WebsocketsEventType
    event_id: Optional[str] = None
    logid: Optional[str] = None


class WebsocketsErrorEvent(WebsocketsEvent):
    type: WebsocketsEventType = WebsocketsEventType.ERROR
    data: CozeAPIError


class WebsocketsBaseClient(abc.ABC):
    class State(str, Enum):
        """
        initialized, connecting, connected, closing, closed
        """

        INITIALIZED = "initialized"
        CONNECTING = "connecting"
        CONNECTED = "connected"
        CLOSING = "closing"
        CLOSED = "closed"

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
        self._state = self.State.INITIALIZED
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

        self._input_queue: queue.Queue[Optional[WebsocketsEvent]] = queue.Queue()
        self._ws: Optional[websockets.sync.client.ClientConnection] = None
        self._send_thread: Optional[threading.Thread] = None
        self._receive_thread: Optional[threading.Thread] = None
        self._completed_events = set()
        self._completed_event = threading.Event()

    @contextmanager
    def __call__(self):
        try:
            self.connect()
            yield self
        finally:
            self.close()

    def connect(self):
        if self._state != self.State.INITIALIZED:
            raise ValueError(f"Cannot connect in {self._state.value} state")
        self._state = self.State.CONNECTING
        headers = {
            "Authorization": f"Bearer {self._auth.token}",
            "X-Coze-Client-User-Agent": coze_client_user_agent(),
            **(self._headers or {}),
        }
        try:
            self._ws = websockets.sync.client.connect(
                self._ws_url,
                user_agent_header=user_agent(),
                additional_headers=headers,
            )
            self._state = self.State.CONNECTED
            log_info("[%s] connected to websocket", self._path)

            self._send_thread = threading.Thread(target=self._send_loop)
            self._receive_thread = threading.Thread(target=self._receive_loop)
            self._send_thread.start()
            self._receive_thread.start()
        except InvalidStatus as e:
            raise CozeAPIError(None, f"{e}", e.response.headers.get("x-tt-logid")) from e

    def wait(self, events: Optional[List[WebsocketsEventType]] = None, wait_all=True) -> None:
        if events is None:
            events = self._wait_events
        self._wait_completed(events, wait_all=wait_all)

    def on(self, event_type: WebsocketsEventType, handler: Callable):
        self._on_event[event_type] = handler

    def close(self) -> None:
        if self._state not in (self.State.CONNECTED, self.State.CONNECTING):
            return
        self._state = self.State.CLOSING
        self._close()
        self._state = self.State.CLOSED

    def _send_loop(self) -> None:
        try:
            while True:
                if event := self._input_queue.get():
                    self._send_event(event)
                self._input_queue.task_done()
        except Exception as e:
            self._handle_error(e)

    def _receive_loop(self) -> None:
        try:
            while True:
                if not self._ws:
                    log_debug("[%s] empty websocket conn, close", self._path)
                    break

                data = self._ws.recv()
                message = json.loads(data)
                event_type = message.get("type")
                log_debug("[%s] receive event, type=%s, event=%s", self._path, event_type, data)

                if handler := self._on_event.get(event_type):
                    if event := self._load_all_event(message):
                        handler(self, event)
                        self._completed_events.add(event_type)
                        self._completed_event.set()
        except Exception as e:
            self._handle_error(e)

    def _load_all_event(self, message: Dict) -> Optional[WebsocketsEvent]:
        event_id = message.get("event_id") or ""
        event_type = message.get("type") or ""
        logid = message.get("logid") or ""
        data = message.get("data") or {}
        if event_type == WebsocketsEventType.ERROR.value:
            code, msg = data.get("code") or 0, data.get("msg") or ""
            return WebsocketsErrorEvent.model_validate(
                {
                    "event_id": event_id,
                    "logid": logid,
                    "data": CozeAPIError(code, msg, logid),
                }
            )
        return self._load_event(message)

    @abc.abstractmethod
    def _load_event(self, message: Dict) -> Optional[WebsocketsEvent]: ...

    def _wait_completed(self, events: List[WebsocketsEventType], wait_all: bool) -> None:
        while True:
            if wait_all:
                # 所有事件都需要完成
                if self._completed_events == set(events):
                    break
            else:
                # 任意一个事件完成即可
                if any(event in self._completed_events for event in events):
                    break
            self._completed_event.wait()
            self._completed_event.clear()

    def _handle_error(self, error: Exception) -> None:
        if handler := self._on_event.get(WebsocketsEventType.ERROR):
            handler(self, error)
        else:
            raise error

    def _close(self) -> None:
        log_info("[%s] connect closed", self._path)
        if self._send_thread:
            self._send_thread.join()
        if self._receive_thread:
            self._receive_thread.join()

        if self._ws:
            self._ws.close()
            self._ws = None

        while not self._input_queue.empty():
            self._input_queue.get()

        if handler := self._on_event.get(WebsocketsEventType.CLOSED):
            handler(self)

    def _send_event(self, event: WebsocketsEvent) -> None:
        log_debug("[%s] send event, type=%s", self._path, event.type.value)
        if self._ws:
            self._ws.send(event.model_dump_json())


class WebsocketsBaseEventHandler(object):
    def on_client_error(self, cli: "WebsocketsBaseClient", e: Exception):
        log_error(f"Client Error occurred: {str(e)}")
        log_error(f"Stack trace:\n{traceback.format_exc()}")

    def on_error(self, cli: "WebsocketsBaseClient", e: Exception):
        log_error(f"Error occurred: {str(e)}")
        log_error(f"Stack trace:\n{traceback.format_exc()}")

    def on_closed(self, cli: "WebsocketsBaseClient"):
        pass

    def to_dict(self, origin: Dict[WebsocketsEventType, Callable]):
        res = {
            WebsocketsEventType.CLIENT_ERROR: self.on_client_error,
            WebsocketsEventType.ERROR: self.on_error,
            WebsocketsEventType.CLOSED: self.on_closed,
        }
        res.update(origin)
        return res


class AsyncWebsocketsBaseClient(abc.ABC):
    class State(str, Enum):
        """
        initialized, connecting, connected, closing, closed
        """

        INITIALIZED = "initialized"
        CONNECTING = "connecting"
        CONNECTED = "connected"
        CLOSING = "closing"
        CLOSED = "closed"

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
        self._state = self.State.INITIALIZED
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
        self._ws: Optional[websockets.asyncio.client.ClientConnection] = None
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
        if self._state != self.State.INITIALIZED:
            raise ValueError(f"Cannot connect in {self._state.value} state")
        self._state = self.State.CONNECTING
        headers = {
            "Authorization": f"Bearer {self._auth.token}",
            "X-Coze-Client-User-Agent": coze_client_user_agent(),
            **(self._headers or {}),
        }
        try:
            self._ws = await websockets.asyncio.client.connect(
                self._ws_url,
                user_agent_header=user_agent(),
                additional_headers=headers,
            )
            self._state = self.State.CONNECTED
            log_info("[%s] connected to websocket", self._path)

            self._send_task = asyncio.create_task(self._send_loop())
            self._receive_task = asyncio.create_task(self._receive_loop())
        except InvalidStatus as e:
            raise CozeAPIError(None, f"{e}", e.response.headers.get("x-tt-logid")) from e

    async def wait(self, events: Optional[List[WebsocketsEventType]] = None, wait_all=True) -> None:
        if events is None:
            events = self._wait_events
        await self._wait_completed(events, wait_all=wait_all)

    def on(self, event_type: WebsocketsEventType, handler: Callable):
        self._on_event[event_type] = handler

    async def close(self) -> None:
        if self._state not in (self.State.CONNECTED, self.State.CONNECTING):
            return
        self._state = self.State.CLOSING
        await self._close()
        self._state = self.State.CLOSED

    async def _send_loop(self) -> None:
        try:
            while True:
                event = await self._input_queue.get()
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
                    if event := self._load_all_event(message):
                        await handler(self, event)
        except Exception as e:
            await self._handle_error(e)

    def _load_all_event(self, message: Dict) -> Optional[WebsocketsEvent]:
        event_id = message.get("event_id") or ""
        event_type = message.get("type") or ""
        logid = message.get("logid") or ""
        data = message.get("data") or {}
        if event_type == WebsocketsEventType.ERROR.value:
            code, msg = data.get("code") or 0, data.get("msg") or ""
            return WebsocketsErrorEvent.model_validate(
                {
                    "event_id": event_id,
                    "logid": logid,
                    "data": CozeAPIError(code, msg, logid),
                }
            )
        return self._load_event(message)

    @abc.abstractmethod
    def _load_event(self, message: Dict) -> Optional[WebsocketsEvent]: ...

    async def _wait_completed(self, wait_events: List[WebsocketsEventType], wait_all: bool) -> None:
        future: asyncio.Future[None] = asyncio.Future()
        completed_events = set()

        def _wrap_handler(event_type: WebsocketsEventType, original_handler):
            async def wrapped(client, event):
                # 先执行原始处理函数
                if original_handler:
                    await original_handler(client, event)

                # 再检查完成条件
                completed_events.add(event_type)
                if wait_all:
                    # 所有事件都需要完成
                    if completed_events == set(wait_events):
                        if not future.done():
                            future.set_result(None)
                else:
                    # 任意一个事件完成即可
                    if not future.done():
                        future.set_result(None)

            return wrapped

        # 为每个指定的事件类型包装处理函数
        origin_handlers = {}
        for event_type in wait_events:
            original_handler = self._on_event.get(event_type)
            origin_handlers[event_type] = original_handler
            self._on_event[event_type] = _wrap_handler(event_type, original_handler)

        try:
            # 等待直到满足完成条件
            await future
        finally:
            # 恢复所有原来的处理函数
            for event_type in wait_events:
                if original_handler := origin_handlers.get(event_type):
                    self._on_event[event_type] = original_handler

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
    async def on_client_error(self, cli: "WebsocketsBaseClient", e: Exception):
        log_error(f"Client Error occurred: {str(e)}")
        log_error(f"Stack trace:\n{traceback.format_exc()}")

    async def on_error(self, cli: "AsyncWebsocketsBaseClient", e: CozeAPIError):
        log_error(f"Error occurred: {str(e)}")
        log_error(f"Stack trace:\n{traceback.format_exc()}")

    async def on_closed(self, cli: "AsyncWebsocketsBaseClient"):
        pass

    def to_dict(self, origin: Dict[WebsocketsEventType, Callable]):
        res = {
            WebsocketsEventType.CLIENT_ERROR: self.on_client_error,
            WebsocketsEventType.ERROR: self.on_error,
            WebsocketsEventType.CLOSED: self.on_closed,
        }
        res.update(origin)
        return res
