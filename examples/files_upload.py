"""
This example describes how to upload files.
"""

import os
import sys

from cozepy import COZE_COM_BASE_URL, Coze, Stream, TokenAuth, WorkflowEvent, WorkflowEventType  # noqa

# Get an access_token through personal access token or oauth.
coze_api_token = os.getenv("COZE_API_TOKEN")
# The default access is api.coze.com, but if you need to access api.coze.cn,
# please use base_url to configure the api endpoint to access
coze_api_base = os.getenv("COZE_API_BASE") or COZE_COM_BASE_URL

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

file_path = sys.argv[1] if len(sys.argv) > 1 else "/path/image.jpg"

file = coze.files.upload(file=file_path)
print(f"uploaded file: {file.id}\n   {file}")
