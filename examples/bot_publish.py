"""
This example is for describing how to create a bot, update a bot and publish a bot to the API.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

from cozepy import (
    COZE_CN_BASE_URL,
    BotPromptInfo,
    ChatEventType,
    Coze,
    DeviceOAuthApp,
    Message,
    MessageContentType,
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
# Whether to print detailed logs
is_debug = os.getenv("DEBUG")

if is_debug:
    setup_logging(logging.DEBUG)


# Call the upload file interface to get the avatar id.
avatar_path = "/path/avatar.jpg" if len(sys.argv) < 2 else sys.argv[1]
avatar = coze.files.upload(file=Path(avatar_path))

# Invoke the create interface to create a bot in the draft status.
bot = coze.bots.create(
    # The bot should exist under a space and your space id needs configuration.
    space_id=workspace_id,
    # Bot name
    name="translator bot",
    # Bot avatar
    icon_file_id=avatar.id,
    # Bot system prompt
    prompt_info=BotPromptInfo(prompt="your are a translator, translate the following text from English to Chinese"),
)

# Call the publish api to publish the bot on the api channel.
coze.bots.publish(bot_id=bot.bot_id)

# Developers can also modify the bot configuration and republish it.
coze.bots.update(
    bot_id=bot.bot_id,
    name="translator bot 2.0",
    prompt_info=BotPromptInfo(prompt="your are a translator, translate the following text from Chinese to English"),
)
coze.bots.publish(bot_id=bot.bot_id, connector_ids=["1024"])

# Call the coze.chat.stream method to create a chat. The create method is a streaming
# chat and will return a Chat Iterator. Developers should iterate the iterator to get
# chat event and handle them.
for event in coze.chat.stream(
    # The published bot's id
    bot_id=bot.bot_id,
    # biz user id, maybe random string
    user_id="user id",
    # user input
    additional_messages=[Message.build_user_question_text("chinese")],
):
    if (
        event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA
        and event.message.content_type == MessageContentType.TEXT
    ):
        print(event.message.content, end="")
