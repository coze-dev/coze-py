"""
This example is about how to create a dataset.
"""

import logging
import os

from cozepy import (  # noqa
    COZE_COM_BASE_URL,
    Coze,
    CreateDatasetResp,
    DocumentFormatType,
    TokenAuth,
    setup_logging,
)

# Get an access_token through personal access token or oauth.
coze_api_token = os.getenv("COZE_API_TOKEN") or "your access token"
# The default access is api.coze.com, but if you need to access api.coze.cn,
# please use base_url to configure the api endpoint to access
coze_api_base = os.getenv("COZE_API_BASE") or COZE_COM_BASE_URL
# workspace id
workspace_id = os.getenv("COZE_WORKSPACE_ID") or "your workspace id"
# Whether to print detailed logs
is_debug = os.getenv("DEBUG")

if is_debug:
    setup_logging(logging.DEBUG)

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

res = coze.datasets.create(
    name="test",
    space_id=workspace_id,
)
print(f"Create dataset: {res.dataset_id}")
