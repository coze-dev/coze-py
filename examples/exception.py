"""
This example is for illustrating how to handle the abnormal errors in the process of using the sdk.
"""

import os
from typing import Optional

from cozepy import (
    COZE_CN_BASE_URL,
    Coze,
    CozeAPIError,
    DeviceOAuthApp,
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


# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=get_coze_api_token()), base_url=get_coze_api_base())

# Invoke the create interface to create a bot in the draft status.
try:
    bot = coze.bots.create(
        # The bot should exist under a space and your space id needs configuration.
        space_id="workspace id",
        # Bot name
        name="translator bot",
    )
except CozeAPIError as e:
    print(e.code, e.msg, e.logid)
    raise  # for example, re-raise the error
