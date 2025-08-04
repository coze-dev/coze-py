"""
示例：更新会话名称

本示例演示如何使用Coze SDK更新指定会话的名称。
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

# 示例：更新会话名称
# 假设我们有一个会话ID
new_name = "新的会话名称"

# 更新会话名称
updated_conversation = coze.conversations.update(conversation_id=conversation_id, name=new_name)

print("会话更新成功：")
print(f"会话ID: {updated_conversation.id}")
print(f"新名称: {updated_conversation.name}")
print(f"更新时间: {updated_conversation.updated_at}")
