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
    # The default access is api.coze.com, but if you need to access api.coze.cn,
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


def cal_latency(latency_list: List[int]) -> str:
    if latency_list is None or len(latency_list) == 0:
        return "0"
    if len(latency_list) == 1:
        return f"{latency_list[0]}"
    res = latency_list.copy()
    res.sort()
    return "%2d" % ((sum(res[:-1]) * 1.0) / (len(res) - 1))


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
    text = os.getenv("COZE_TEXT") or "为什么深圳比北京大"

    # Initialize Coze client
    coze = Coze(
        auth=TokenAuth(coze_api_token),
        base_url=coze_api_base,
    )

    times = 50
    text_latency = []
    for i in range(times):
        logid, text, latency = await test_latency(coze, bot_id, text)
        text_latency.append(latency)
        print(f"[latency.text] {i}, latency: {cal_latency(text_latency)} ms, log: {logid}, text: {text}")


if __name__ == "__main__":
    asyncio.run(main())
