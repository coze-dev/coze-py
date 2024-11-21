"""
This example is about how to list conversation.
"""

import logging
import os

from cozepy import (  # noqa
    COZE_COM_BASE_URL,
    BotPromptInfo,
    ChatEventType,
    Coze,
    Message,
    MessageContentType,
    MessageRole,
    TokenAuth,
    setup_logging,
)

# Get an access_token through personal access token or oauth.
coze_api_token = os.getenv("COZE_API_TOKEN")
# The default access is api.coze.com, but if you need to access api.coze.cn,
# please use base_url to configure the api endpoint to access
coze_api_base = os.getenv("COZE_API_BASE") or COZE_COM_BASE_URL
# coze bot id
coze_bot_id = os.getenv("COZE_BOT_ID") or "input your bot id"
# Whether to print detailed logs
is_debug = os.getenv("DEBUG")

if is_debug:
    setup_logging(logging.DEBUG)

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

conversations = coze.conversations.list(bot_id=coze_bot_id, page_size=2)

for conversation in conversations:
    print("conversation[id]", conversation.id)
    print("conversation[created_at]", conversation.created_at)
    print("conversation[last_section_id]", conversation.last_section_id)
    print("")

for page in conversations.iter_pages():
    print("items", page.items)
