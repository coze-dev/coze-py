"""
How to configure timeout
"""

import os

import httpx

from cozepy import COZE_COM_BASE_URL, AsyncHTTPClient, SyncHTTPClient

# Get an access_token through personal access token or oauth.
coze_api_token = os.getenv("COZE_API_TOKEN")
# The default access is api.coze.com, but if you need to access api.coze.cn,
# please use base_url to configure the api endpoint to access
coze_api_base = os.getenv("COZE_API_BASE") or COZE_COM_BASE_URL

from cozepy import Coze, AsyncCoze, TokenAuth, Message, ChatStatus, MessageContentType, ChatEventType  # noqa

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
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base, http_client=http_client)

# The same is true for asynchronous clients
async_coze = AsyncCoze(
    auth=TokenAuth(token=coze_api_token),
    base_url=coze_api_base,
    http_client=AsyncHTTPClient(
        timeout=httpx.Timeout(
            # 600s timeout on elsewhere
            timeout=600.0,
            # 5s timeout on connect
            connect=5.0,
        )
    ),
)
