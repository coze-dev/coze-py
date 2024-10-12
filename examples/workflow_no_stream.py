"""
This example describes how to use the workflow interface to chat.
"""

import os  # noqa

# Get an access_token through pat or oauth.
api_coze_token = os.getenv("COZE_API_TOKEN")

from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType  # noqa

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=api_coze_token))

# Create a workflow instance in Coze, copy the last number from the web link as the workflow's ID.
workflow_id = "workflow id"

# Call the coze.workflows.runs.create method to create a workflow run. The create method
# is a non-streaming chat and will return a WorkflowRunResult class.
workflow = coze.workflows.runs.create(
    workflow_id=workflow_id,
)

print("workflow.data", workflow.data)
