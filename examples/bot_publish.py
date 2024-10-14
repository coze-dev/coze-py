"""
This example is for describing how to create a bot, update a bot and publish a bot to the API.
"""

import os  # noqa
from pathlib import Path

# Get an access_token through personal access token oroauth.
api_coze_token = os.getenv("COZE_API_TOKEN")

from cozepy import Coze, TokenAuth, BotPromptInfo, Message, ChatEventType, MessageContentType  # noqa

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=api_coze_token))

# Call the upload file interface to get the avatar id.
avatar = coze.files.upload(file=Path("/path/avatar.jpg"))

# Invoke the create interface to create a bot in the draft status.
bot = coze.bots.create(
    # The bot should exist under a space and your space id needs configuration.
    space_id="workspace id",
    # Bot name
    name="translator bot",
    # Bot avatar
    icon_file_id=avatar.id,
    # Bot system prompt
    prompt_info=BotPromptInfo(prompt="your are a translator, translate the following text from English to Chinese"),
)

# Call the publish interface to publish the bot on the api channel.
coze.bots.publish(bot_id=bot.bot_id)

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
        and event.message.content.type == MessageContentType.TEXT
    ):
        print(event.message.content, end="")
