"""
How to configure timeout
"""

import os
from typing import Optional

import httpx

from cozepy import (  # noqa
    COZE_CN_BASE_URL,
    AsyncCoze,
    AsyncHTTPClient,
    ChatEventType,
    ChatStatus,
    Coze,
    DeviceOAuthApp,
    Message,
    MessageContentType,
    SyncHTTPClient,
    TokenAuth,
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


# Coze client is built on httpx, and supports passing a custom httpx.Client when initializing
# Coze, and setting a timeout on the httpx.Client
http_client = SyncHTTPClient(
    timeout=httpx.Timeout(
        # 600s timeout on elsewhere
        timeout=600.0,
        # 5s timeout on connect
        connect=5.0,
    )
)
# Init the Coze client through the access_token and custom timeout http client.
coze = Coze(auth=TokenAuth(token=get_coze_api_token()), base_url=get_coze_api_base(), http_client=http_client)

# The same is true for asynchronous clients
async_coze = AsyncCoze(
    auth=TokenAuth(token=get_coze_api_token()),
    base_url=get_coze_api_base(),
    http_client=AsyncHTTPClient(
        timeout=httpx.Timeout(
            # 600s timeout on elsewhere
            timeout=600.0,
            # 5s timeout on connect
            connect=5.0,
        )
    ),
)
