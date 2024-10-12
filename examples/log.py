"""
This example is for the configuration of logs.
"""

import logging
import os

from cozepy import setup_logging

# open debug logging, default is warning
setup_logging(level=logging.DEBUG)

# Get an access_token through pat or oauth.
api_coze_token = os.getenv("COZE_API_TOKEN")

from cozepy import Coze, TokenAuth, BotPromptInfo, Message, ChatEventType, MessageContentType  # noqa

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=api_coze_token or "mock"))

# Invoke the create interface to create a bot in the draft status.
bot = coze.bots.create(
    # The bot should exist under a space and your workspace id needs configuration.
    space_id="workspace id",
    # Bot name
    name="translator bot",
)
