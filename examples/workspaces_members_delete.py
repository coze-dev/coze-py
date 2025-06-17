"""
This example is about how to create workspace members.
"""

import logging
import os
from typing import Optional

from cozepy import (
    COZE_CN_BASE_URL,
    Coze,
    DeviceOAuthApp,
    TokenAuth,
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
# workspace id
workspace_id = os.getenv("COZE_WORKSPACE_ID")
# user id admin
user_id_admin = os.getenv("COZE_USER_ID_ADMIN")
# user id member
user_id_member = os.getenv("COZE_USER_ID_MEMBER")


def setup_examples_logger():
    coze_log = os.getenv("COZE_LOG")
    if coze_log:
        setup_logging(logging.getLevelNamesMapping().get(coze_log.upper(), logging.INFO))


setup_examples_logger()

user_ids = []
if user_id_admin:
    user_ids.append(user_id_admin)
if user_id_member:
    user_ids.append(user_id_member)


delete_workspaces_members_resp = coze.workspaces.members.delete(
    workspace_id=workspace_id,
    user_ids=user_ids,
)

print("workspaces.members.delete", delete_workspaces_members_resp.model_dump_json(indent=2))
print("logid", delete_workspaces_members_resp.response.logid)
