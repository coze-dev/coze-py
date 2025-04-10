"""
This example is about how to use the streaming interface to start a chat request
and handle chat events
"""

import logging
import os
import sys
from typing import Optional

from cozepy import (
    COZE_CN_BASE_URL,
    ChatEventType,
    Coze,
    DeviceOAuthApp,
    Message,
    MessageObjectString,
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
# Get the workflow id
workflow_id = os.getenv("COZE_WORKFLOW_ID") or "workflow id"
# Get the bot id
bot_id = os.getenv("COZE_BOT_ID")
# Whether to print detailed logs
is_debug = os.getenv("DEBUG")

if is_debug:
    setup_logging(logging.DEBUG)


conversation = coze.conversations.create()

# Call the upload interface to upload a picture requiring text recognition, and
# obtain the file_id of the picture.
file_path = sys.argv[1] if len(sys.argv) > 1 else "/path/image.jpg"
file = coze.files.upload(file=file_path)

# Call the coze.chat.stream method to create a chat. The create method is a streaming
# chat and will return a Chat Iterator. Developers should iterate the iterator to get
# chat event and handle them.
for event in coze.workflows.chat.stream(
    workflow_id=workflow_id,
    bot_id=bot_id,
    conversation_id=conversation.id,
    additional_messages=[
        Message.build_user_question_objects(
            [
                MessageObjectString.build_text("What text is on the picture?"),
                MessageObjectString.build_image(file_id=file.id),
            ]
        ),
    ],
):
    if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
        print(event.message.content, end="", flush=True)

    if event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
        print()
        print("token usage:", event.chat.usage.token_count)
