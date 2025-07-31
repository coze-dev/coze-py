#!/usr/bin/env python3
"""
更新Bot渠道审核结果示例

本示例演示如何使用Coze SDK更新Bot在特定渠道的审核结果。
"""

import os
from typing import Optional

from cozepy import COZE_CN_BASE_URL, Coze, DeviceOAuthApp, TokenAuth
from cozepy.connectors.bots import AuditStatus


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

# 更新Bot审核结果为通过
resp = coze.connectors.bots.update(
    bot_id=coze_bot_id,
    connector_id="1024",  # API渠道
    audit_status=AuditStatus.APPROVED,
)
print("logid:", resp.response.logid)
