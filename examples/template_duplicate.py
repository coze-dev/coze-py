"""
This example demonstrates how to duplicate a template.
"""

import os

from cozepy import Coze
from cozepy.auth import TokenAuth
from cozepy.config import COZE_COM_BASE_URL

# Get an access_token through personal access token or oauth.
coze_api_token = os.getenv("COZE_API_TOKEN")
# The default access is api.coze.com, but if you need to access api.coze.cn,
# please use base_url to configure the api endpoint to access
coze_api_base = os.getenv("COZE_API_BASE") or COZE_COM_BASE_URL
# workspace id
workspace_id = os.getenv("COZE_WORKSPACE_ID")
# template id
template_id = os.getenv("COZE_TEMPLATE_ID")

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)


res = coze.templates.duplicate(template_id=template_id, workspace_id=workspace_id)
print("entity_id:", res.entity_id)
print("entity_type:", res.entity_type)
