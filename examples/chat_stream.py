"""
This example is about how to use the streaming interface to start a chat request
and handle chat events
"""

import os

from cozepy import COZE_COM_BASE_URL

# Get an access_token through personal access token or oauth.
coze_api_token = os.getenv("COZE_API_TOKEN")
# The default access is api.coze.com, but if you need to access api.coze.cn,
# please use base_url to configure the api endpoint to access
coze_api_base = os.getenv("COZE_API_BASE") or COZE_COM_BASE_URL

from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType, ChatEventType  # noqa

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

# Create a bot instance in Coze, copy the last number from the web link as the bot's ID.
bot_id = os.getenv("COZE_BOT_ID") or "bot id"
# The user id identifies the identity of a user. Developers can use a custom business ID
# or a random string.
user_id = "user id"

# Call the coze.chat.stream method to create a chat. The create method is a streaming
# chat and will return a Chat Iterator. Developers should iterate the iterator to get
# chat event and handle them.
for event in coze.chat.stream(
    bot_id=bot_id,
    user_id=user_id,
    additional_messages=[
        Message.build_user_question_text("Who are you?"),
        Message.build_assistant_answer("I am Bot by Coze."),
        Message.build_user_question_text("1+2=? And tell me your name."),
    ],
):
    if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
        print(event.message.content, end="")
