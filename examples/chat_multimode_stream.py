"""
This example is about how to use the streaming interface to start a chat request
with image upload and handle chat events
"""

import os  # noqa
import sys

from cozepy import COZE_COM_BASE_URL

# Get an access_token through pat or oauth.
api_coze_token = os.getenv("COZE_API_TOKEN")
api_base = os.getenv("COZE_API_BASE") or COZE_COM_BASE_URL

from cozepy import Coze, TokenAuth, Message, ChatEventType, MessageObjectString  # noqa

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=api_coze_token), base_url=api_base)

# Create a bot instance in Coze, copy the last number from the web link as the bot's ID.
bot_id = os.getenv("COZE_BOT_ID")
# The user id identifies the identity of a user. Developers can use a custom business ID
# or a random string.
user_id = "user id"

from pathlib import Path  # noqa

# Call the upload interface to upload a picture requiring text recognition, and
# obtain the file_id of the picture.
file_path = sys.argv[1] if len(sys.argv) > 1 else "/path/image.jpg"
file = coze.files.upload(file=Path(file_path))

# Call the coze.chat.stream method to create a chat. The create method is a streaming
# chat and will return a Chat Iterator. Developers should iterate the iterator to get
# chat event and handle them.
for event in coze.chat.stream(
    bot_id=bot_id,
    user_id=user_id,
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
        message = event.message
        print(event.message.content, end="")
