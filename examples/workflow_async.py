"""
This example describes how to use the workflow with async.
"""

import logging
import os
import time
from typing import Optional

from cozepy import COZE_CN_BASE_URL, Coze, DeviceOAuthApp, TokenAuth, WorkflowExecuteStatus, setup_logging


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
# Whether to print detailed logs
is_debug = os.getenv("DEBUG")
if is_debug:
    setup_logging(logging.DEBUG)


# Create a workflow instance in Coze, copy the last number from the web link as the workflow's ID.
workflow_id = os.getenv("COZE_WORKFLOW_ID") or "your workflow id"

# Call the coze.workflows.runs.create method to create a workflow run. The create method
# is a non-streaming chat and will return a WorkflowRunResult class.
workflow_run = coze.workflows.runs.create(workflow_id=workflow_id, is_async=True)

print("Start async workflow run:", workflow_run.execute_id)

while True:
    run_history = coze.workflows.runs.run_histories.retrieve(
        workflow_id=workflow_id, execute_id=workflow_run.execute_id
    )
    if run_history.execute_status == WorkflowExecuteStatus.FAIL:
        print("Workflow run fail:", run_history.error_message)
        break
    elif run_history.execute_status == WorkflowExecuteStatus.RUNNING:
        print("Workflow still running, sleep 1s and continue")
        time.sleep(1)
        continue
    else:
        print("Workflow run success:", run_history.output)
        break
