"""
This example describes how to use the workflow with async.
"""

import logging
import os
import time

from cozepy import COZE_COM_BASE_URL, Coze, TokenAuth, WorkflowExecuteStatus, setup_logging

# Get an access_token through personal access token or oauth.
coze_api_token = os.getenv("COZE_API_TOKEN")
# The default access is api.coze.com, but if you need to access api.coze.cn,
# please use base_url to configure the api endpoint to access
coze_api_base = os.getenv("COZE_API_BASE") or COZE_COM_BASE_URL
# Whether to print detailed logs
is_debug = os.getenv("DEBUG")

if is_debug:
    setup_logging(logging.DEBUG)

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

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
