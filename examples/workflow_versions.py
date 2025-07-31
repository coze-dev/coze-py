#!/usr/bin/env python3

import os

from cozepy import Coze, TokenAuth

# Get an access token through personal access token or oauth.
coze_api_token = os.getenv("COZE_API_TOKEN")
# The default access is api.coze.com, but if you need to access api.coze.cn,
# please use base_url to configure the api endpoint to access
coze = Coze(auth=TokenAuth(token=coze_api_token))  # type: ignore

# Workflow ID
workflow_id = os.getenv("COZE_WORKFLOW_ID")

if not workflow_id:
    raise ValueError("COZE_WORKFLOW_ID is required")

# List workflow versions
versions = coze.workflows.versions.list(workflow_id=workflow_id)

# Print version information
for version in versions:
    print(f"Version: {version.version}")
    print(f"Description: {version.description}")
    print(f"Created at: {version.created_at}")
    print(f"Updated at: {version.updated_at}")
    print(f"Creator: {version.creator.name} ({version.creator.id})")
    print("-" * 40)


# Asynchronously list workflow versions
async def async_list_versions():
    # List workflow versions
    versions = await coze.workflows.versions.list(workflow_id=workflow_id)

    # Print version information
    async for version in versions:
        print(f"Version: {version.version}")
        print(f"Description: {version.description}")
        print(f"Created at: {version.created_at}")
        print(f"Updated at: {version.updated_at}")
        print(f"Creator: {version.creator.name} ({version.creator.id})")
        print("-" * 40)


if __name__ == "__main__":
    # Run async example
    import asyncio

    asyncio.run(async_list_versions())
