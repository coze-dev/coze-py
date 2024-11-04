"""
This example is about how to list workspaces.
"""

import os

from cozepy import COZE_COM_BASE_URL, BotPromptInfo, ChatEventType, Coze, Message, MessageContentType, TokenAuth  # noqa

# Get an access_token through personal access token or oauth.
coze_api_token = os.getenv("COZE_API_TOKEN")
# The default access is api.coze.com, but if you need to access api.coze.cn,
# please use base_url to configure the api endpoint to access
coze_api_base = os.getenv("COZE_API_BASE") or COZE_COM_BASE_URL

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)


# Call the api to get workspace list.
workspaces = coze.workspaces.list()
for workspace in workspaces:
    # workspaces is an iterator. Traversing workspaces will automatically turn pages and
    # get all workspace results.
    print("Get workspace", workspace.id, workspace.name)
