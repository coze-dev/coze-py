"""
This example is for describing how to update a bot.
"""

import logging
import os
from typing import Optional

from cozepy import (
    COZE_CN_BASE_URL,
    BotSuggestReplyInfo,
    Coze,
    DeviceOAuthApp,
    SuggestReplyMode,
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


# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=get_coze_api_token()), base_url=get_coze_api_base())
# workspace id
workspace_id = os.getenv("COZE_WORKSPACE_ID") or "your workspace id"
# bot id
bot_id = os.getenv("COZE_BOT_ID") or "your bot id"
# Whether to print detailed logs
is_debug = os.getenv("DEBUG")

if is_debug:
    setup_logging(logging.DEBUG)

bot_update = coze.bots.update(
    bot_id=bot_id,
    suggest_reply_info=BotSuggestReplyInfo(
        reply_mode=SuggestReplyMode.ENABLE, customized_prompt="generate suggest reply"
    ),
)
print("update logid", bot_update.response.logid)
