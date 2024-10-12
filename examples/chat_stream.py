"""
This example is about how to use the streaming interface to start a chat request
and handle chat events
"""

import os  # noqa

# Get an access_token through pat or oauth.
api_coze_token = os.getenv("COZE_API_TOKEN")

from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType, ChatEventType  # noqa

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=api_coze_token))

# Create a bot instance in Coze, copy the last number from the web link as the bot's ID.
bot_id = "bot id"
# The user id identifies the identity of a user. Developers can use a custom business ID
# or a random string.
user_id = "user id"

# Call the coze.chat.stream method to create a chat. The create method is a streaming
# chat and will return a Chat Iterator. Developers should iterate the iterator to get
# chat event and handle them.
for event in coze.chat.stream(
    bot_id=bot_id, user_id=user_id, additional_messages=[Message.build_user_question_text("How are you?")]
):
    if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
        message = event.message
        print(f"role={message.role}, content={message.content}")
