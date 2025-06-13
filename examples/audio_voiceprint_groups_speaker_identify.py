"""
This example is for describing how to speaker_identify voiceprint group feature.
"""

import logging
import os
from typing import Optional

from cozepy import (
    COZE_CN_BASE_URL,
    Coze,
    DeviceOAuthApp,
    TokenAuth,
    setup_logging,
)


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
# voiceprint group id
voiceprint_group_id = os.getenv("COZE_VOICEPRINT_GROUP_ID")
# voiceprint group feature file
voiceprint_group_feature_file = os.getenv("COZE_VOICEPRINT_GROUP_FEATURE_FILE")


def setup_examples_logger():
    coze_log = os.getenv("COZE_LOG")
    if coze_log:
        setup_logging(logging.getLevelNamesMapping().get(coze_log.upper(), logging.INFO))


setup_examples_logger()


speaker_identify_resp = coze.audio.voiceprint_groups.speaker_identify(
    group_id=voiceprint_group_id,
    file=voiceprint_group_feature_file,
)
for item in speaker_identify_resp.feature_score_list:
    print(item.model_dump_json(indent=2))
print("logid", speaker_identify_resp.response.logid)
