"""
This example describes how to use the workflow async run and retrieve the run history.
"""

import logging
import os
import time
from typing import Optional

from cozepy import (
    COZE_CN_BASE_URL,
    Coze,
    DeviceOAuthApp,
    TokenAuth,
    WorkflowExecuteStatus,
)
from cozepy.log import setup_logging


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
workflow_id = os.getenv("COZE_WORKFLOW_ID")


def setup_examples_logger():
    coze_log = os.getenv("COZE_LOG")
    if coze_log:
        setup_logging(logging.getLevelNamesMapping().get(coze_log.upper(), logging.INFO))


setup_examples_logger()


workflow_run_result = coze.workflows.runs.create(workflow_id=workflow_id, is_async=True)
run_history = None
while True:
    time.sleep(1)
    run_history = coze.workflows.runs.run_histories.retrieve(
        workflow_id=workflow_id,
        execute_id=workflow_run_result.execute_id,
    )
    if run_history.execute_status == WorkflowExecuteStatus.SUCCESS:
        break
    time.sleep(1)

node_execute_uuids = [
    node_execute_status.node_execute_uuid for node_execute_status in run_history.node_execute_status.values()
]
assert node_execute_uuids

for node_execute_uuid in node_execute_uuids:
    node_execute_history = coze.workflows.runs.run_histories.execute_nodes.retrieve(
        workflow_id=workflow_id,
        execute_id=workflow_run_result.execute_id,
        node_execute_uuid=node_execute_uuid,
    )
    print("node_execute_history:", node_execute_history)
