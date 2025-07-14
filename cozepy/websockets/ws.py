import abc
import asyncio
import json
import logging
import queue
import sys
import threading
import traceback
from abc import ABC
from contextlib import asynccontextmanager, contextmanager
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union, get_type_hints

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

from cozepy.exception import CozeAPIError
from cozepy.log import log_debug, log_error, log_info, log_warning, logger
from cozepy.model import CozeModel, DynamicStrEnum
from cozepy.request import Requester
from cozepy.util import get_methods, get_model_default, remove_url_trailing_slash
from cozepy.version import coze_client_user_agent, user_agent


class WebsocketsEventType(DynamicStrEnum):
    # common
    CLIENT_ERROR = "client_error"  # sdk error
    CLOSED = "closed"  # connection closed

    # error
    ERROR = "error"  # 发生错误

    # v1/audio/speech
    # req
    SPEECH_UPDATE = "speech.update"  # 更新语音合成配置
    INPUT_TEXT_BUFFER_APPEND = "input_text_buffer.append"  # 流式输入文字
    INPUT_TEXT_BUFFER_COMPLETE = "input_text_buffer.complete"  # 提交文字
    # resp
    # v1/audio/speech
    SPEECH_CREATED = "speech.created"  # 语音合成连接成功
    SPEECH_UPDATED = "speech.updated"  # 配置更新完成
    INPUT_TEXT_BUFFER_COMPLETED = "input_text_buffer.completed"  # input_text_buffer 提交完成
    SPEECH_AUDIO_UPDATE = "speech.audio.update"  # 合成增量语音
    SPEECH_AUDIO_COMPLETED = "speech.audio.completed"  # 合成完成

    # v1/audio/transcriptions
    # req
    TRANSCRIPTIONS_UPDATE = "transcriptions.update"  # 更新语音识别配置
    INPUT_AUDIO_BUFFER_APPEND = "input_audio_buffer.append"  # 流式上传音频片段
    INPUT_AUDIO_BUFFER_COMPLETE = "input_audio_buffer.complete"  # 提交音频
    INPUT_AUDIO_BUFFER_CLEAR = "input_audio_buffer.clear"  # 清除缓冲区音频
    # resp
    TRANSCRIPTIONS_CREATED = "transcriptions.created"  # 连接成功
    TRANSCRIPTIONS_UPDATED = "transcriptions.updated"  # 配置更新成功
    INPUT_AUDIO_BUFFER_COMPLETED = "input_audio_buffer.completed"  # 音频提交完成
    INPUT_AUDIO_BUFFER_CLEARED = "input_audio_buffer.cleared"  # 音频清除成功
    TRANSCRIPTIONS_MESSAGE_UPDATE = "transcriptions.message.update"  # 识别出文字
    TRANSCRIPTIONS_MESSAGE_COMPLETED = "transcriptions.message.completed"  # 识别完成

    # v1/chat
    # req
    CHAT_UPDATE = "chat.update"  # 更新对话配置
    # INPUT_AUDIO_BUFFER_APPEND = "input_audio_buffer.append"  # 流式上传音频片段
    # INPUT_AUDIO_BUFFER_COMPLETE = "input_audio_buffer.complete"  # 提交音频
    # INPUT_AUDIO_BUFFER_CLEAR = "input_audio_buffer.clear"  # 清除缓冲区音频
    CONVERSATION_MESSAGE_CREATE = "conversation.message.create"  # 手动提交对话内容
    CONVERSATION_CLEAR = "conversation.clear"  # 清除上下文
    CONVERSATION_CHAT_SUBMIT_TOOL_OUTPUTS = "conversation.chat.submit_tool_outputs"  # 提交端插件执行结果
    CONVERSATION_CHAT_CANCEL = "conversation.chat.cancel"  # 打断智能体输出
    INPUT_TEXT_GENERATE_AUDIO = "input_text.generate_audio"  # 提交文字用于语音合成
    # resp
    CHAT_CREATED = "chat.created"  # 对话连接成功
    CHAT_UPDATED = "chat.updated"  # 对话配置成功
    CONVERSATION_CHAT_CREATED = "conversation.chat.created"  # 对话开始
    CONVERSATION_CHAT_IN_PROGRESS = "conversation.chat.in_progress"  # 对话正在处理
    CONVERSATION_MESSAGE_DELTA = "conversation.message.delta"  # 增量消息
    CONVERSATION_AUDIO_SENTENCE_START = "conversation.audio.sentence_start"  # 增量语音字幕
    CONVERSATION_AUDIO_DELTA = "conversation.audio.delta"  # 增量语音
    CONVERSATION_MESSAGE_COMPLETED = "conversation.message.completed"  # 消息完成
    CONVERSATION_AUDIO_COMPLETED = "conversation.audio.completed"  # 语音回复完成
    CONVERSATION_CHAT_COMPLETED = "conversation.chat.completed"  # 对话完成
    CONVERSATION_CHAT_FAILED = "conversation.chat.failed"  # 对话失败
    # INPUT_AUDIO_BUFFER_COMPLETED = "input_audio_buffer.completed"  # 音频提交完成
    # INPUT_AUDIO_BUFFER_CLEARED = "input_audio_buffer.cleared"  # 音频清除成功
    CONVERSATION_CLEARED = "conversation.cleared"  # 上下文清除完成
    CONVERSATION_CHAT_CANCELED = "conversation.chat.canceled"  # 智能体输出中断
    CONVERSATION_AUDIO_TRANSCRIPT_UPDATE = "conversation.audio_transcript.update"  # 用户语音识别字幕
    CONVERSATION_AUDIO_TRANSCRIPT_COMPLETED = "conversation.audio_transcript.completed"  # 用户语音识别完成
    CONVERSATION_CHAT_REQUIRES_ACTION = "conversation.chat.requires_action"  # 端插件请求
    INPUT_AUDIO_BUFFER_SPEECH_STARTED = "input_audio_buffer.speech_started"  # 用户开始说话
    INPUT_AUDIO_BUFFER_SPEECH_STOPPED = "input_audio_buffer.speech_stopped"  # 用户结束说话


class WebsocketsEvent(CozeModel, ABC):
    class Detail(BaseModel):
        logid: Optional[str] = None
        # if event_type=error, origin_message is the original input message
        origin_message: Optional[str] = None

    event_type: WebsocketsEventType
    id: Optional[str] = None
    detail: Optional[Detail] = None


class WebsocketsErrorEvent(WebsocketsEvent):
    """发生错误"""

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

    @lru_cache(maxsize=128)
    def get_event_class(
        self,
        event_type: str,
    ) -> Tuple[Optional[Type[WebsocketsEvent]], Optional[Type[BaseModel]]]:
        event_class = self._event_type_to_class.get(event_type)
        if not event_class:
            return None, None

        type_hints = get_type_hints(event_class)
        data_type = type_hints.get("data")
        if data_type:
            return event_class, data_type
        return event_class, None

    def create_event(self, path: str, message: Dict) -> Optional[WebsocketsEvent]:
        event_id = message.get("id") or ""
        detail = WebsocketsEvent.Detail.model_validate(message.get("detail") or {})
        event_type = message.get("event_type") or ""
        data = message.get("data") or {}

        event_class, data_class = self.get_event_class(event_type)
        if not event_class:
            log_warning("[%s] unknown event, type=%s, logid=%s", path, event_type, detail.logid)
            return None

        event_data = {
            "id": event_id,
            "detail": detail,
        }

        if data and data_class:
            event_data["data"] = data_class.model_validate(data)
        return event_class.model_validate(event_data)


def _log_receive_event(path: str, event_type: Optional[str], data: Union[str, bytes]):
    if logger.level > logging.DEBUG:
        return
    if event_type and event_type == "conversation.audio.delta":
        message = json.loads(data)
        if message and message.get("data") and message.get("data", {}).get("content"):
            message["data"]["content"] = f"<length: {len(message['data']['content'])}>"
            log_debug("[%s] receive event, type=%s, event=%s", path, event_type, json.dumps(message))
            return
    log_debug("[%s] receive event, type=%s, event=%s", path, event_type, data)


def _log_send_event(path: str, event: WebsocketsEvent):
    if logger.level > logging.DEBUG:
        return
    if event.event_type == WebsocketsEventType.INPUT_AUDIO_BUFFER_APPEND:
        log_debug(
            "[%s] send event, type=%s, event=%s",
            path,
            event.event_type.value,
            json.dumps(event._dump_without_delta()),  # type: ignore
        )
    else:
        log_debug(
            "[%s] send event, type=%s, event=%s",
            path,
            event.event_type.value,
            event.model_dump_json(exclude_none=True),
        )


class WebsocketsBaseClient(abc.ABC):
    class State(DynamicStrEnum):
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
        event_factory: WebsocketsEventFactory,
        query: Optional[Dict[str, str]] = None,
        on_event: Optional[Dict[WebsocketsEventType, Callable]] = None,
        wait_events: Optional[List[WebsocketsEventType]] = None,
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
        self._event_factory = event_factory

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
                    _log_receive_event(self._path, event_type, data)

                    event = self._parse_event(message)
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

    def _parse_event(self, message: Dict) -> Optional[WebsocketsEvent]:
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
        return self._event_factory.create_event(self._path, message)

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
        self._ws.send(event.model_dump_json(exclude_none=True))


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
    class State(DynamicStrEnum):
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
        event_factory: WebsocketsEventFactory,
        query: Optional[Dict[str, str]] = None,
        on_event: Optional[Dict[WebsocketsEventType, Callable]] = None,
        wait_events: Optional[List[WebsocketsEventType]] = None,
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
        self._event_factory = event_factory

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
                _log_receive_event(self._path, event_type, data)

                handler = self._on_event.get(event_type)
                event = self._parse_event(message)
                if handler and event:
                    await handler(self, event)
        except Exception as e:
            await self._handle_error(e)

    def _parse_event(self, message: Dict) -> Optional[WebsocketsEvent]:
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
        return self._event_factory.create_event(self._path, message)

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
        _log_send_event(self._path, event)
        await self._ws.send(event.model_dump_json(exclude_none=True))


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
