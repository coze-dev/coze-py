"""
This example describes how to use the workflow run_histories.
"""

import os
from typing import Optional

from cozepy import COZE_CN_BASE_URL, Coze, DeviceOAuthApp, Stream, TokenAuth, WorkflowEvent, WorkflowEventType  # noqa


def get_coze_api_base() -> str:
    # The default access is api.coze.cn, but if you need to access api.coze.com,
    # please use base_url to configure the api endpoint to access
    coze_api_base = os.getenv("COZE_API_BASE")
    if coze_api_base:
        return coze_api_base

    return COZE_CN_BASE_URL  # default


def get_coze_api_token(workspace_id: Optional[str] = None) -> str:
    # Get an access_token through personal access token or oauth.
    coze_api_token = os.getenv("COZE_API_TOKEN")
    if coze_api_token:
        return coze_api_token

    coze_api_base = get_coze_api_base()

    device_oauth_app = DeviceOAuthApp(client_id="57294420732781205987760324720643.app.coze", base_url=coze_api_base)
    device_code = device_oauth_app.get_device_code(workspace_id)
    print(f"Please Open: {device_code.verification_url} to get the access token")
    return device_oauth_app.get_access_token(device_code=device_code.device_code, poll=True).access_token


# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=get_coze_api_token()), base_url=get_coze_api_base())
# Create a workflow instance in Coze, copy the last number from the web link as the workflow's ID.
workflow_id = os.getenv("COZE_WORKFLOW_ID") or "workflow id"
execute_id = os.getenv("COZE_EXECUTE_ID") or "execute id"

run_history = coze.workflows.runs.run_histories.retrieve(workflow_id=workflow_id, execute_id=execute_id)
print("run_history:", run_history)
print("logid:", run_history.response.logid)
