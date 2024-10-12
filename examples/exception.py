"""
This example is for illustrating how to handle the abnormal errors in the process of using the sdk.
"""

import os  # noqa

# Get an access_token through pat or oauth.
api_coze_token = os.getenv("COZE_API_TOKEN")

from cozepy import Coze, TokenAuth, BotPromptInfo, Message, ChatEventType, MessageContentType, CozeAPIError  # noqa

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=api_coze_token))

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
