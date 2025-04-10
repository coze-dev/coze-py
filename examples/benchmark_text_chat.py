import asyncio
import json
import logging
import os
import time
from typing import List, Optional

from cozepy import (
    COZE_CN_BASE_URL,
    ChatEventType,
    Coze,
    DeviceOAuthApp,
    Message,
    TokenAuth,
    setup_logging,
)


def get_coze_api_base() -> str:
    # The default access is api.coze.cn, but if you need to access api.coze.com,
    # please use base_url to configure the api endpoint to access
    coze_api_base = os.getenv("COZE_API_BASE")
    if coze_api_base:
        return coze_api_base

    return COZE_CN_BASE_URL  # default


def get_coze_api_token(workspace_id: Optional[str] = None) -> str:
    # Get an access_token through personal access token or oauth.
    coze_api_token = os.getenv("COZE_API_TOKEN")
    if coze_api_token:
        return coze_api_token

    coze_api_base = get_coze_api_base()

    device_oauth_app = DeviceOAuthApp(client_id="57294420732781205987760324720643.app.coze", base_url=coze_api_base)
    device_code = device_oauth_app.get_device_code(workspace_id)
    print(f"Please Open: {device_code.verification_url} to get the access token")
    return device_oauth_app.get_access_token(device_code=device_code.device_code, poll=True).access_token


def setup_examples_logger():
    coze_log = os.getenv("COZE_LOG")
    if coze_log:
        setup_logging(logging.getLevelNamesMapping().get(coze_log.upper(), logging.INFO))


def get_current_time_ms():
    return int(time.time() * 1000)


setup_examples_logger()

kwargs = json.loads(os.getenv("COZE_KWARGS") or "{}")


def cal_latency(current: int, latency_list: List[int]) -> str:
    if latency_list is None or len(latency_list) == 0:
        return "No latency data"
    if len(latency_list) == 1:
        return f"P99={latency_list[0]}ms, P90={latency_list[0]}ms, AVG={latency_list[0]}ms"

    # 对延迟数据进行排序
    sorted_latency = sorted(latency_list)
    length = len(sorted_latency)

    def fix_index(index):
        if index < 0:
            return 0
        if index >= length:
            return length - 1
        return index

    # 计算 P99
    p99_index = fix_index(round(length * 0.99) - 1)
    p99 = sorted_latency[p99_index]

    # 计算 P90
    p90_index = fix_index(round(length * 0.90) - 1)
    p90 = sorted_latency[p90_index]

    # 计算平均值
    avg = sum(sorted_latency) / length

    return f"P99={p99}ms, P90={p90}ms, AVG={avg:.2f}ms, CURRENT={current}ms"


async def test_latency(coze: Coze, bot_id: str, text: str) -> (str, str, int):
    start = get_current_time_ms()
    stream = coze.chat.stream(
        bot_id=bot_id,
        user_id="user id",
        additional_messages=[
            Message.build_user_question_text(text),
        ],
    )
    for event in stream:
        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            return stream.response.logid, event.message.content, get_current_time_ms() - start


async def main():
    coze_api_token = get_coze_api_token()
    coze_api_base = get_coze_api_base()
    bot_id = os.getenv("COZE_BOT_ID")
    text = os.getenv("COZE_TEXT") or "讲个笑话"

    # Initialize Coze client
    coze = Coze(
        auth=TokenAuth(coze_api_token),
        base_url=coze_api_base,
    )

    times = 100
    text_latency = []
    for i in range(times):
        logid, first_text, latency = await test_latency(coze, bot_id, text)
        text_latency.append(latency)
        print(f"[latency.text] {i}, latency: {cal_latency(latency, text_latency)}, log: {logid}, text: {first_text}")


if __name__ == "__main__":
    asyncio.run(main())
