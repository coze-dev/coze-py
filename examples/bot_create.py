"""
This example demonstrates how to create a bot with advanced configurations including knowledge base, plugins, and workflows.
"""

import logging
import os
import sys
from typing import Optional

from cozepy import (
    COZE_CN_BASE_URL,
    BotModelInfo,
    BotOnboardingInfo,
    BotPromptInfo,
    BotSuggestReplyInfo,
    Coze,
    DeviceOAuthApp,
    PluginIDList,
    SuggestReplyMode,
    TokenAuth,
    WorkflowIDList,
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
# workspace id
workspace_id = os.getenv("COZE_WORKSPACE_ID") or "your workspace id"
avatar_path = "" if len(sys.argv) < 2 else sys.argv[1]
# Whether to print detailed logs
is_debug = os.getenv("DEBUG")

if is_debug:
    setup_logging(logging.DEBUG)

file_id = None
if avatar_path:
    file = coze.files.upload(file=avatar_path)
    file_id = file.id
    print("create avatar file: ", avatar_path, file)

# 创建具有高级配置的智能体
bot = coze.bots.create(
    space_id=workspace_id,
    name="高级智能助手",
    description="一个具备知识库、插件和工作流的高级智能助手",
    icon_file_id=file_id,
    prompt_info=BotPromptInfo(prompt="你是一个专业的智能助手，能够回答各种问题并提供准确的信息。"),
    onboarding_info=BotOnboardingInfo(
        prologue="你好！我是你的智能助手，有什么可以帮助你的吗？",
        suggested_questions=["今天天气怎么样？", "请介绍一下人工智能", "如何学习编程？"],
    ),
    suggest_reply_info=BotSuggestReplyInfo(
        reply_mode=SuggestReplyMode.CUSTOMIZED, customized_prompt="根据用户的问题，生成3个相关的后续问题建议"
    ),
    model_info_config=BotModelInfo(
        model_id="doubao-pro-128k", temperature=0.7, max_tokens=2000, response_format="markdown"
    ),
    plugin_id_list=PluginIDList(
        id_list=[
            PluginIDList.PluginIDInfo(
                plugin_id="7379227817307013129",  # 链接读取
                api_id="7379227817307029513",  # LinkReaderPlugin
            )
        ]
    ),
    workflow_id_list=WorkflowIDList(
        ids=[
            WorkflowIDList.WorkflowIDInfo(
                id="mock id"  # test workflow
            )
        ]
    ),
)
print("create advanced bot", bot.model_dump_json(indent=2))
print("logid", bot.response.logid)
