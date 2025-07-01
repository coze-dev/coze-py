import json
import os
import socket
import ssl
import time
from dataclasses import dataclass
from typing import Dict

from httpx._transports.default import HTTPTransport

from cozepy import (
    COZE_CN_BASE_URL,
    ChatEventType,
    Coze,
    Message,
    SyncHTTPClient,
    TokenAuth,
)


@dataclass
class RequestTiming:
    url: str
    start_time: float = 0  # 0. 开始请求时间
    end_time: float = 0  # 9. 结束请求时间
    # 可以计算总时间
    dns_start: float = 0  # 1. socket.create_connection 之前
    dns_end: float = 0  # 2. socket.create_connection 之后
    # 可以计算 dns 时间
    tls_start: float = 0  # 3. ssl.SSLContext 之前
    tls_end: float = 0  # 4. ssl.SSLContext 之后
    # 可以计算 tls 时间
    request_start: float = 0  # 5. httpx.request 之前, 开始请求时间
    request_end: float = 0  # 6. httpx.request 之后, 结束请求时间
    # 可以计算请求的时间
    response_read_start: float = 0  # 7. httpx.response.read 之前, 开始读取响应时间
    response_read_end: float = 0  # 8. httpx.response.read 之后, 结束读取响应时间
    # 可以计算响应的时间

    @property
    def dns_time(self) -> float:
        if self.dns_start and self.dns_end:
            return self.dns_end - self.dns_start
        return 0

    @property
    def tls_time(self) -> float:
        if self.tls_start and self.tls_end:
            return self.tls_end - self.tls_start
        return 0

    @property
    def request_time(self) -> float:
        if self.request_end and self.request_start:
            return self.request_end - self.request_start
        return 0

    @property
    def response_time(self) -> float:
        if self.response_read_end and self.response_read_start:
            return self.response_read_end - self.response_read_start
        return 0

    @property
    def total_time(self) -> float:
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        return 0

    def to_dict(self) -> Dict[str, float]:
        return {
            "dns_time": round(self.dns_time * 1000, 2),
            "tls_time": round(self.tls_time * 1000, 2),
            "request_time": round(self.request_time * 1000, 2),
            "response_time": round(self.response_time * 1000, 2),
            "total_time": round(self.total_time * 1000, 2),
        }

    def __str__(self) -> str:
        times = self.to_dict()
        return (
            f"URL: {self.url}\n"
            f"DNS解析时间: {times['dns_time']}ms\n"
            f"TLS握手时间: {times['tls_time']}ms\n"
            f"请求发送时间: {times['request_time']}ms\n"
            f"响应接收时间: {times['response_time']}ms\n"
            f"总请求时间: {times['total_time']}ms\n"
        )


timings = {"data": []}


class TimingHTTPTransport(HTTPTransport):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timings: Dict[str, RequestTiming] = {}

    def handle_request(self, request):
        timing = RequestTiming(url=str(request.url), start_time=time.time())

        # 保存当前请求的计时对象
        request_id = id(request)
        self.timings[request_id] = timing
        timings["data"].append(timing)

        # 重写socket创建函数以捕获DNS解析时间
        original_create_connection = socket.create_connection

        def timed_create_connection(*args, **kwargs):
            timing.dns_start = time.time()  # 1
            conn = original_create_connection(*args, **kwargs)
            timing.dns_end = time.time()  # 2
            return conn

        # 重写SSL上下文的wrap_socket以捕获TLS握手时间
        original_wrap_socket = ssl.SSLContext.wrap_socket
        original_wrap_bio = ssl.SSLContext.wrap_bio

        def timed_wrap_socket(self, *args, **kwargs):
            timing.tls_start = time.time()  # 3.1
            sock = original_wrap_socket(self, *args, **kwargs)
            timing.tls_end = time.time()  # 4.1
            return sock

        def timed_wrap_bio(self, *args, **kwargs):
            timing.tls_start = time.time()  # 3.2
            bio = original_wrap_bio(self, *args, **kwargs)
            timing.tls_end = time.time()  # 4.2
            return bio

        try:
            # 作用: 在发起网络请求之前，会先调用 timed_create_connection 函数，该函数会记录DNS解析的开始和结束时间。
            socket.create_connection = timed_create_connection
            # 作用: 在发起TLS握手之前，会先调用 timed_wrap_socket 函数，该函数会记录TLS握手的开始和结束时间。
            ssl.SSLContext.wrap_socket = timed_wrap_socket
            # 作用: 在发起TLS握手之前，会先调用 timed_wrap_bio 函数，该函数会记录TLS握手的开始和结束时间。
            ssl.SSLContext.wrap_bio = timed_wrap_bio

            # 记录请求开始时间
            timing.request_start = time.time()  # 5

            # 发送请求
            response = super().handle_request(request)

            # 记录请求结束时间
            timing.request_end = time.time()  # 6

            # 包装响应对象以捕获完整的响应时间
            original_read = response.read
            original_iter_bytes = response.iter_bytes

            def timed_read(*args, **kwargs):
                timing.response_read_start = time.time()  # 7.1
                result = original_read(*args, **kwargs)
                timing.response_read_end = time.time()  # 8.1
                return result

            def timed_iter_bytes(*args, **kwargs):
                timing.response_read_start = time.time()  # 7.2
                result = original_iter_bytes(*args, **kwargs)
                timing.response_read_end = time.time()  # 8.2
                return result

            response.read = timed_read
            response.iter_bytes = timed_iter_bytes

            return response

        finally:
            # 恢复原始函数
            socket.create_connection = original_create_connection
            ssl.SSLContext.wrap_socket = original_wrap_socket
            ssl.SSLContext.wrap_bio = original_wrap_bio

            timing.end_time = time.time()  # 9


def test_coze(coze: Coze):
    start = time.time() * 1000
    stream = coze.chat.stream(
        bot_id=bot_id,
        user_id="user_id",
        additional_messages=[
            Message.build_user_question_text("hello"),
        ],
        headers={"x-tt-trace": "1"},
    )

    first_token_time = 0
    content = ""
    for event in stream:
        if first_token_time == 0 and event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            if event.message.content != "":
                content = event.message.content
            first_token_time = time.time() * 1000
        else:
            continue

    return {
        # "logid": stream.response.logid,
        "e2e latency": first_token_time - start,
        "content": content,
        "timing": timings["data"][-1].to_dict(),
    }


coze_api_base = os.getenv("COZE_API_BASE") or COZE_CN_BASE_URL
coze_api_token = os.getenv("COZE_API_TOKEN")
bot_id = os.getenv("COZE_BOT_ID") or "bot id"
transport = TimingHTTPTransport()
coze = Coze(
    auth=TokenAuth(token=coze_api_token), base_url=coze_api_base, http_client=SyncHTTPClient(transport=transport)
)

print(json.dumps(test_coze(coze), indent="  "))
print(json.dumps(test_coze(coze), indent="  "))
print(json.dumps(test_coze(coze), indent="  "))
