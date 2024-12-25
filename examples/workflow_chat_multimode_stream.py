"""
This example is about how to use the streaming interface to start a chat request
and handle chat events
"""

import logging
import os
import sys

from cozepy import (
    COZE_COM_BASE_URL,
    ChatEventType,
    Coze,
    JWTAuth,
    JWTOAuthApp,
    Message,
    MessageObjectString,
    setup_logging,
)

# Get the workflow id
workflow_id = os.getenv("COZE_WORKFLOW_ID") or "workflow id"
# Get the bot id
bot_id = os.getenv("COZE_BOT_ID")
# Whether to print detailed logs
is_debug = os.getenv("DEBUG")

if is_debug:
    setup_logging(logging.DEBUG)


def init_coze_client() -> Coze:
    # client ID
    jwt_oauth_client_id = os.getenv("COZE_JWT_OAUTH_CLIENT_ID")
    # path to the private key file (usually with .pem extension)
    jwt_oauth_private_key_file_path = os.getenv("COZE_JWT_OAUTH_PRIVATE_KEY_FILE_PATH")
    # public key id
    jwt_oauth_public_key_id = os.getenv("COZE_JWT_OAUTH_PUBLIC_KEY_ID")
    # private key
    jwt_oauth_private_key = ""
    with open(jwt_oauth_private_key_file_path, "r") as f:
        jwt_oauth_private_key = f.read()

    # The default access is api.coze.com, but if you need to access api.coze.cn,
    # please use base_url to configure the api endpoint to access
    coze_api_base = os.getenv("COZE_API_BASE") or COZE_COM_BASE_URL

    jwt_oauth_app = JWTOAuthApp(
        client_id=jwt_oauth_client_id,
        private_key=jwt_oauth_private_key,
        public_key_id=jwt_oauth_public_key_id,
        base_url=coze_api_base,
    )

    return Coze(auth=JWTAuth(base_url=coze_api_base, oauth_app=jwt_oauth_app), base_url=coze_api_base)


# Init the Coze client through the access_token.
coze = init_coze_client()

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
