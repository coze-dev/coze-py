"""
删除会话示例

本示例演示如何使用Coze SDK删除指定的会话。
删除会话后，会话及其中的所有消息都将被永久删除，无法恢复。
"""

import logging
import os
from typing import Optional

from cozepy import COZE_CN_BASE_URL, Coze, DeviceOAuthApp, TokenAuth, setup_logging


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


# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=get_coze_api_token()), base_url=get_coze_api_base())
# coze bot id
coze_bot_id = os.getenv("COZE_BOT_ID") or "input your bot id"
conversation_id = os.getenv("COZE_CONVERSATION_ID") or "your_conversation_id"
# Whether to print detailed logs
is_debug = os.getenv("DEBUG")

if is_debug:
    setup_logging(logging.DEBUG)

# 删除会话
resp = coze.conversations.delete(conversation_id=conversation_id)
print(f"成功删除会话: {conversation_id}")
print(f"响应日志ID: {resp.response.logid}")
