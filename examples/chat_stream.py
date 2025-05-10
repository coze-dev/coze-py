"""
This example is about how to use the streaming interface to start a chat request
and handle chat events
"""

import json
import logging
import os
from typing import Optional

from cozepy import COZE_CN_BASE_URL, ChatEventType, Coze, DeviceOAuthApp, Message, TokenAuth, setup_logging  # noqa


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

# Create a bot instance in Coze, copy the last number from the web link as the bot's ID.
bot_id = os.getenv("COZE_BOT_ID") or "bot id"
# The user id identifies the identity of a user. Developers can use a custom business ID
# or a random string.
user_id = "user id"
# Whether to print detailed logs
is_debug = os.getenv("DEBUG")

parameters = json.loads(os.getenv("COZE_PARAMETERS") or "{}")

if is_debug:
    setup_logging(logging.DEBUG)

# Call the coze.chat.stream method to create a chat. The create method is a streaming
# chat and will return a Chat Iterator. Developers should iterate the iterator to get
# chat event and handle them.
is_first_reasoning_content = True
is_first_content = True
stream = coze.chat.stream(
    bot_id=bot_id,
    user_id=user_id,
    additional_messages=[
        Message.build_user_question_text("Tell a 500-word story."),
    ],
    parameters=parameters,
)
print("logid:", stream.response.logid)
for event in stream:
    if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
        if event.message.reasoning_content:
            if is_first_reasoning_content:
                is_first_reasoning_content = not is_first_reasoning_content
                print("----- reasoning_content start -----\n> ", end="", flush=True)
            print(event.message.reasoning_content, end="", flush=True)
        else:
            if is_first_content and not is_first_reasoning_content:
                is_first_content = not is_first_content
                print("----- reasoning_content end -----")
            print(event.message.content, end="", flush=True)

    if event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
        print()
        print("token usage:", event.chat.usage.token_count)

    if event.event == ChatEventType.CONVERSATION_CHAT_FAILED:
        print()
        print("chat failed", event.chat.last_error)
        break
