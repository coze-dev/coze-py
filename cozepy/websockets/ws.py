import abc
import asyncio
import json
import queue
import sys
import threading
import traceback
from abc import ABC
from contextlib import asynccontextmanager, contextmanager
from enum import Enum
from multiprocessing.util import sub_warning
from typing import Any, Callable, Dict, List, Optional, Set, Type, get_type_hints

if sys.version_info >= (3, 8):
    # note: >=3.7,<3.8 not support asyncio
    from websockets import InvalidStatus
    from websockets.asyncio.client import ClientConnection as AsyncWebsocketClientConnection
    from websockets.asyncio.client import connect as asyncio_connect
else:
    # 警告: 当前Python版本不支持asyncio websockets
    # 如果Python版本小于3.8,则不支持异步websockets功能
    import warnings

    warnings.warn("asyncio websockets requires Python >= 3.8")

    class AsyncWebsocketClientConnection(object):
        def recv(self, *args, **kwargs):
            pass

        def send(self, *args, **kwargs):
            pass

        def close(self, *args, **kwargs):
            pass

    def asyncio_connect(*args, **kwargs):
        pass

    class InvalidStatus(object):
        pass


import websockets.sync.client
from pydantic import BaseModel

from cozepy import CozeAPIError
from cozepy.log import log_debug, log_error, log_info
from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import get_methods, get_model_default, remove_url_trailing_slash
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
    SPEECH_CREATED = "speech.created"  # after speech created
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
    TRANSCRIPTIONS_CREATED = "transcriptions.created"  # after transcriptions created
    INPUT_AUDIO_BUFFER_COMPLETED = "input_audio_buffer.completed"  # received `input_audio_buffer.complete` event
    TRANSCRIPTIONS_MESSAGE_UPDATE = "transcriptions.message.update"  # received `transcriptions.update` event
    TRANSCRIPTIONS_MESSAGE_COMPLETED = "transcriptions.message.completed"  # all audio received, can close connection

    # v1/chat
    # req
    # INPUT_AUDIO_BUFFER_APPEND = "input_audio_buffer.append" # send audio to server
    # INPUT_AUDIO_BUFFER_COMPLETE = "input_audio_buffer.complete" # no audio send, start chat
    CHAT_UPDATE = "chat.update"  # send chat config to server
    CONVERSATION_CHAT_SUBMIT_TOOL_OUTPUTS = "conversation.chat.submit_tool_outputs"  # send tool outputs to server
    CONVERSATION_CHAT_CANCEL = "conversation.chat.cancel"  # send cancel chat to server
    CONVERSATION_MESSAGE_CREATE = "conversation.message.create"  # send text or string_object chat to server
    # resp
    CHAT_CREATED = "chat.created"
    CHAT_UPDATED = "chat.updated"
    # INPUT_AUDIO_BUFFER_COMPLETED = "input_audio_buffer.completed" # received `input_audio_buffer.complete` event
    CONVERSATION_CHAT_CREATED = "conversation.chat.created"  # audio ast completed, chat started
    CONVERSATION_CHAT_IN_PROGRESS = "conversation.chat.in_progress"
    CONVERSATION_MESSAGE_DELTA = "conversation.message.delta"  # get agent text message update
    CONVERSATION_CHAT_REQUIRES_ACTION = "conversation.chat.requires_action"  # need plugin submit
    INPUT_AUDIO_BUFFER_SPEECH_STARTED = "input_audio_buffer.speech_started"  # 用户开始说话, 此事件表示服务端识别到用户正在说话。只有在 server_vad 模式下，才会返回此事件。
    INPUT_AUDIO_BUFFER_SPEECH_STOPPED = "input_audio_buffer.speech_stopped"  # 用户结束说话, 此事件表示服务端识别到用户已停止说话。只有在 server_vad 模式下，才会返回此事件。
    CONVERSATION_AUDIO_TRANSCRIPT_COMPLETED = "conversation.audio_transcript.completed"
    CONVERSATION_MESSAGE_COMPLETED = "conversation.message.completed"
    CONVERSATION_AUDIO_DELTA = "conversation.audio.delta"  # get agent audio message update
    CONVERSATION_AUDIO_COMPLETED = "conversation.audio.completed"
    CONVERSATION_CHAT_COMPLETED = "conversation.chat.completed"  # all message received, can close connection
    CONVERSATION_CHAT_FAILED = "conversation.chat.failed"
    CONVERSATION_CHAT_CANCELED = "conversation.chat.canceled"  # chat canceled
    CONVERSATION_AUDIO_TRANSCRIPT_UPDATE = (
        "conversation.audio_transcript.update"  # 用户语音识别字幕, 用户语音识别的中间值，每次返回都是全量文本。
    )


class WebsocketsEvent(CozeModel, ABC):
    class Detail(BaseModel):
        logid: Optional[str] = None
        # if event_type=error, origin_message is the original input message
        origin_message: Optional[str] = None

    event_type: WebsocketsEventType
    id: Optional[str] = None
    detail: Optional[Detail] = None


class WebsocketsErrorEvent(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.ERROR
    data: CozeAPIError


class LimitConfig(BaseModel):
    # 周期的时长，单位为秒。例如设置为 10 秒，则以 10 秒作为一个周期。
    period: Optional[int] = None
    # 周期内，最大返回包数量。
    max_frame_num: Optional[int] = None


class InputAudio(BaseModel):
    # 输入音频的格式，支持 pcm、wav、ogg。默认为 wav。
    format: Optional[str]
    # 输入音频的编码，支持 pcm、opus、g711a、g711u。默认为 pcm。如果音频编码格式为 g711a 或 g711u，format 请设置为 pcm。
    codec: Optional[str]
    # 输入音频的采样率，默认是 24000。支持 8000、16000、22050、24000、32000、44100、48000。如果音频编码格式 codec 为 g711a 或 g711u，音频采样率需设置为 8000。
    sample_rate: Optional[int]
    # 输入音频的声道数，支持 1（单声道）、2（双声道）。默认是 1（单声道）。
    channel: Optional[int]
    # 输入音频的位深，默认是 16，支持8、16和24。
    bit_depth: Optional[int]


class OpusConfig(BaseModel):
    # 输出 opus 的码率，默认 48000。
    bitrate: Optional[int] = None
    # 输出 opus 是否使用 CBR 编码，默认为 false。
    use_cbr: Optional[bool] = None
    # 输出 opus 的帧长，默认是 10。可选值：2.5、5、10、20、40、60
    frame_size_ms: Optional[float] = None
    # 输出音频限流配置，默认不限制。
    limit_config: Optional[LimitConfig] = None


class PCMConfig(BaseModel):
    # 输出 pcm 音频的采样率，默认是 24000。支持 8000、16000、22050、24000、32000、44100、48000。
    sample_rate: Optional[int] = None
    # 输出每个 pcm 包的时长，单位 ms，默认不限制。
    frame_size_ms: Optional[float] = None
    # 输出音频限流配置，默认不限制。
    limit_config: Optional[LimitConfig] = None


class OutputAudio(BaseModel):
    # 输出音频编码，支持 pcm、g711a、g711u、opus。默认是 pcm。当 codec 设置为 pcm、g711a或 g711u时，你可以通过 pcm_config 配置 PCM 音频参数。
    codec: Optional[str]
    # 当 codec 设置为 pcm、g711a 或 g711u 时，用于配置 PCM 音频参数。当 codec 设置为 opus 时，不需要设置此字段
    pcm_config: Optional[PCMConfig] = None
    # 当 codec 设置为 pcm 时，不需要设置此字段。
    opus_config: Optional[OpusConfig] = None
    # 输出音频的语速，取值范围 [-50, 100]，默认为 0。-50 表示 0.5 倍速，100 表示 2 倍速。
    speech_rate: Optional[int] = None
    # 输出音频的音色 ID，默认是柔美女友音色。你可以调用[查看音色列表](https://www.coze.cn/open/docs/developer_guides/list_voices) API 查看当前可用的所有音色 ID。
    voice_id: Optional[str] = None


class WebsocketsEventFactory(object):
    def __init__(self, event_type_to_class: Dict[str, Type[WebsocketsEvent]]):
        self._event_type_to_class = event_type_to_class

    def get_data_type(cls, event_class: WebsocketsEvent) -> Optional[Type[BaseModel]]:
        type_hints = get_type_hints(event_class)
        data_type = type_hints.get("data")
        if data_type:
            return data_type
        return None

    def create_event(self, path: str, message: Dict) -> Optional[WebsocketsEvent]:
        event_id = message.get("id") or ""
        detail = WebsocketsEvent.Detail.model_validate(message.get("detail") or {})
        event_type = message.get("event_type") or ""
        data = message.get("data") or {}

        event_class = self._event_type_to_class.get(event_type)
        if not event_class:
            sub_warning("[%s] unknown event, type=%s, logid=%s", path, event_type, detail.logid)
            return None

        event_data = {
            "id": event_id,
            "detail": detail,
        }

        if data:
            data_class = self.get_data_type(event_class)
            if data_class:
                event_data["data"] = data_class.model_validate(data)
        return event_class.model_validate(event_data)


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
        requester: Requester,
        path: str,
        query: Optional[Dict[str, str]] = None,
        on_event: Optional[Dict[WebsocketsEventType, Callable]] = None,
        wait_events: Optional[List[WebsocketsEventType]] = None,
        event_type_to_class: Optional[Dict[str, Type[WebsocketsEvent]]] = None,
        **kwargs,
    ):
        self._state = self.State.INITIALIZED
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._path = path
        self._ws_url = self._base_url + "/" + path
        if query:
            self._ws_url += "?" + "&".join([f"{k}={v}" for k, v in query.items()])
        self._on_event = on_event.copy() if on_event else {}
        self._headers = kwargs.get("headers")
        self._wait_events = wait_events.copy() if wait_events else []
        self._event_factory = WebsocketsEventFactory(event_type_to_class) if event_type_to_class else None

        self._input_queue: queue.Queue[Optional[WebsocketsEvent]] = queue.Queue()
        self._ws: Optional[websockets.sync.client.ClientConnection] = None
        self._send_thread: Optional[threading.Thread] = None
        self._receive_thread: Optional[threading.Thread] = None
        self._completed_events: Set[WebsocketsEventType] = set()
        self._completed_event = threading.Event()
        self._join_event = threading.Event()

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
            "X-Coze-Client-User-Agent": coze_client_user_agent(),
            **(self._headers or {}),
        }

        self._requester.auth_header(headers)

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
        self._join_event.set()
        self._close()
        self._state = self.State.CLOSED

    def _send_loop(self) -> None:
        try:
            while not self._join_event.is_set():
                try:
                    event = self._input_queue.get(timeout=0.5)
                    self._send_event(event)
                    self._input_queue.task_done()
                except queue.Empty:
                    pass
        except Exception as e:
            self._handle_error(e)

    def _receive_loop(self) -> None:
        try:
            while not self._join_event.is_set():
                if not self._ws:
                    log_debug("[%s] empty websocket conn, close", self._path)
                    break

                try:
                    data = self._ws.recv(timeout=0.5)
                    message = json.loads(data)
                    event_type = message.get("event_type")
                    log_debug("[%s] receive event, type=%s, event=%s", self._path, event_type, data)

                    event = self._load_all_event(message)
                    if event:
                        handler = self._on_event.get(event_type)
                        if handler:
                            handler(self, event)
                        self._completed_events.add(event_type)
                        self._completed_event.set()
                except TimeoutError:
                    pass
        except Exception as e:
            self._handle_error(e)

    def _load_all_event(self, message: Dict) -> Optional[WebsocketsEvent]:
        event_id = message.get("id") or ""
        event_type = message.get("event_type") or ""
        detail = WebsocketsEvent.Detail.model_validate(message.get("detail") or {})
        data = message.get("data") or {}
        if event_type == WebsocketsEventType.ERROR.value:
            code, msg = data.get("code") or 0, data.get("msg") or ""
            return WebsocketsErrorEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                    "data": CozeAPIError(code, msg, WebsocketsEvent.Detail.model_validate(detail).logid),
                }
            )
        if self._event_factory:
            return self._event_factory.create_event(self._path, message)
        return None

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
        handler = self._on_event.get(WebsocketsEventType.ERROR)
        if handler:
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

        handler = self._on_event.get(WebsocketsEventType.CLOSED)
        if handler:
            handler(self)

    def _send_event(self, event: Optional[WebsocketsEvent] = None) -> None:
        if not event or not self._ws:
            return
        log_debug("[%s] send event, type=%s", self._path, event.event_type.value)
        self._ws.send(event.model_dump_json())


def get_event_type_mapping(cls: Any) -> dict:
    res = {}
    method_list = get_methods(cls)
    for method in method_list:
        parameters = method.get("parameters", [])
        for param in parameters:
            if issubclass(param.annotation, WebsocketsEvent):
                event_type = get_model_default(param.annotation, "event_type")
                if event_type:
                    res[event_type] = method.get("function")
                    break
    return res


class WebsocketsBaseEventHandler(object):
    def on_client_error(self, cli: "WebsocketsBaseClient", e: Exception):
        log_error(f"Client Error occurred: {str(e)}")
        log_error(f"Stack trace:\n{traceback.format_exc()}")

    def on_error(self, cli: "WebsocketsBaseClient", e: Exception):
        log_error(f"Error occurred: {str(e)}")
        log_error(f"Stack trace:\n{traceback.format_exc()}")

    def on_closed(self, cli: "WebsocketsBaseClient"):
        pass

    def to_dict(self, origin: Optional[Dict[WebsocketsEventType, Callable]] = None):
        res = {
            WebsocketsEventType.CLIENT_ERROR: self.on_client_error,
            WebsocketsEventType.ERROR: self.on_error,
            WebsocketsEventType.CLOSED: self.on_closed,
        }

        res.update(get_event_type_mapping(self))
        res.update(origin or {})
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
        requester: Requester,
        path: str,
        query: Optional[Dict[str, str]] = None,
        on_event: Optional[Dict[WebsocketsEventType, Callable]] = None,
        wait_events: Optional[List[WebsocketsEventType]] = None,
        event_type_to_class: Optional[Dict[str, Type[WebsocketsEvent]]] = None,
        **kwargs,
    ):
        self._state = self.State.INITIALIZED
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._path = path
        self._ws_url = self._base_url + "/" + path
        if query:
            self._ws_url += "?" + "&".join([f"{k}={v}" for k, v in query.items()])
        self._on_event = on_event.copy() if on_event else {}
        self._headers = kwargs.get("headers")
        self._wait_events = wait_events.copy() if wait_events else []
        self._event_factory = WebsocketsEventFactory(event_type_to_class) if event_type_to_class else None

        self._input_queue: asyncio.Queue[Optional[WebsocketsEvent]] = asyncio.Queue()
        self._ws: Optional[AsyncWebsocketClientConnection] = None
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
            "X-Coze-Client-User-Agent": coze_client_user_agent(),
            **(self._headers or {}),
        }

        await self._requester.async_auth_header(headers)

        try:
            self._ws = await asyncio_connect(
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
                event_type = message.get("event_type")
                log_debug("[%s] receive event, type=%s, event=%s", self._path, event_type, data)

                handler = self._on_event.get(event_type)
                event = self._load_all_event(message)
                if handler and event:
                    await handler(self, event)
        except Exception as e:
            await self._handle_error(e)

    def _load_all_event(self, message: Dict) -> Optional[WebsocketsEvent]:
        event_id = message.get("id") or ""
        event_type = message.get("event_type") or ""
        detail = WebsocketsEvent.Detail.model_validate(message.get("detail") or {})
        data = message.get("data") or {}
        if event_type == WebsocketsEventType.ERROR.value:
            code, msg = data.get("code") or 0, data.get("msg") or ""
            return WebsocketsErrorEvent.model_validate(
                {
                    "id": event_id,
                    "detail": detail,
                    "data": CozeAPIError(code, msg, WebsocketsEvent.Detail.model_validate(detail).logid),
                }
            )
        if self._event_factory:
            return self._event_factory.create_event(self._path, message)
        return None

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
                original_handler = origin_handlers.get(event_type)
                if original_handler:
                    self._on_event[event_type] = original_handler

    async def _handle_error(self, error: Exception) -> None:
        handler = self._on_event.get(WebsocketsEventType.ERROR)
        if handler:
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

        handler = self._on_event.get(WebsocketsEventType.CLOSED)
        if handler:
            await handler(self)

    async def _send_event(self, event: Optional[WebsocketsEvent] = None) -> None:
        if not event or not self._ws:
            return
        if event.event_type == WebsocketsEventType.INPUT_AUDIO_BUFFER_APPEND:
            log_debug(
                "[%s] send event, type=%s, event=%s",
                self._path,
                event.event_type.value,
                json.dumps(event._dump_without_delta()),  # type: ignore
            )
        else:
            log_debug("[%s] send event, type=%s, event=%s", self._path, event.event_type.value, event.model_dump_json())
        await self._ws.send(event.model_dump_json())


class AsyncWebsocketsBaseEventHandler(object):
    async def on_client_error(self, cli: "WebsocketsBaseClient", e: Exception):
        log_error(f"Client Error occurred: {str(e)}")
        log_error(f"Stack trace:\n{traceback.format_exc()}")

    async def on_error(self, cli: "AsyncWebsocketsBaseClient", e: CozeAPIError):
        log_error(f"Error occurred: {str(e)}")
        log_error(f"Stack trace:\n{traceback.format_exc()}")

    async def on_closed(self, cli: "AsyncWebsocketsBaseClient"):
        pass

    def to_dict(self, origin: Optional[Dict[WebsocketsEventType, Callable]] = None):
        res = {
            WebsocketsEventType.CLIENT_ERROR: self.on_client_error,
            WebsocketsEventType.ERROR: self.on_error,
            WebsocketsEventType.CLOSED: self.on_closed,
        }

        res.update(get_event_type_mapping(self))
        res.update(origin or {})
        return res
