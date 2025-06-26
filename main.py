import asyncio
import logging
import os
from typing import Any, Dict

from cozepy.auth import AsyncTokenAuth
from cozepy.chat import Message
from cozepy.config import COZE_CN_BASE_URL
from cozepy.coze import AsyncCoze
from cozepy.request import AsyncHTTPClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def format_headers(headers: Dict[str, Any], title: str) -> str:
    header_lines = [f"=== {title} ==="]
    for name, value in headers.items():
        # 隐藏敏感信息
        if name.lower() in ["authorization", "cookie", "set-cookie"]:
            value = "***HIDDEN***"
        header_lines.append(f"{name}: {value}")
    return "\n".join(header_lines)


def log_request_headers(request):
    headers_dict = dict(request.headers)
    headers_str = format_headers(headers_dict, "请求头")
    logger.info(f"\n{headers_str}")
    logger.info(f"请求方法: {request.method}")
    logger.info(f"请求URL: {request.url}")


def log_response_headers(response):
    """记录响应头"""
    headers_dict = dict(response.headers)
    headers_str = format_headers(headers_dict, "响应头")
    logger.info(f"\n{headers_str}")
    logger.info(f"状态码: {response.status_code}")


async def main():
    token = os.getenv("COZE_API_TOKEN")
    bot_id = os.getenv("COZE_BOT_ID")
    client = AsyncHTTPClient(event_hooks={"request": [log_request_headers], "response": [log_response_headers]})
    coze = AsyncCoze(auth=AsyncTokenAuth(token=token), base_url=COZE_CN_BASE_URL, http_client=client)

    async for chunk in coze.chat.stream(
        bot_id=bot_id,
        user_id="1",
        additional_messages=[Message.build_user_question_text("chat")],
    ):
        print(chunk)


if __name__ == "__main__":
    asyncio.run(main())
