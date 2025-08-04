#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
创建会话示例

本示例演示如何使用Coze SDK创建一个新的会话。
"""

import logging
import os
from typing import Optional

from cozepy import COZE_CN_BASE_URL, Coze, DeviceOAuthApp, Message, TokenAuth, setup_logging


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
# coze bot id
coze_bot_id = os.getenv("COZE_BOT_ID") or "input your bot id"
conversation_id = os.getenv("COZE_CONVERSATION_ID") or "your_conversation_id"
# Whether to print detailed logs
is_debug = os.getenv("DEBUG")

if is_debug:
    setup_logging(logging.DEBUG)


def create_simple_conversation():
    """
    创建一个简单的空会话
    """
    print("=== 创建简单会话 ===")

    # 创建一个空会话
    conversation = coze.conversations.create()

    print(f"会话ID: {conversation.id}")
    print(f"创建时间: {conversation.created_at}")
    print(f"会话名称: {conversation.name}")
    print(f"元数据: {conversation.meta_data}")

    return conversation


def create_conversation_with_name():
    """
    创建带有自定义名称的会话
    """
    print("\n=== 创建带名称的会话 ===")

    # 创建带有自定义名称的会话
    conversation = coze.conversations.create(name="我的测试会话")

    print(f"会话ID: {conversation.id}")
    print(f"会话名称: {conversation.name}")

    return conversation


def create_conversation_with_bot():
    """
    创建绑定到特定Bot的会话
    """
    print("\n=== 创建绑定Bot的会话 ===")

    # 这里使用一个示例Bot ID，实际使用时请替换为你的Bot ID
    bot_id = os.getenv("COZE_BOT_ID") or "your_bot_id_here"

    conversation = coze.conversations.create(bot_id=bot_id, name="绑定Bot的会话")

    print(f"会话ID: {conversation.id}")
    print(f"Bot ID: {conversation.bot_id}")
    print(f"会话名称: {conversation.name}")

    return conversation


def create_conversation_with_messages():
    """
    创建会话并包含初始消息
    """
    print("\n=== 创建带初始消息的会话 ===")

    # 创建包含初始消息的会话
    messages = [
        Message.build_user_question_text("你好，这是一个测试消息"),
        Message.build_assistant_answer("你好！很高兴收到你的消息。"),
    ]

    conversation = coze.conversations.create(messages=messages, name="带初始消息的会话")

    print(f"会话ID: {conversation.id}")
    print(f"会话名称: {conversation.name}")
    print(f"初始消息数量: {len(messages)}")

    return conversation


def create_conversation_with_metadata():
    """
    创建会话并包含自定义元数据
    """
    print("\n=== 创建带元数据的会话 ===")

    # 创建带有自定义元数据的会话
    meta_data = {"source": "example_script", "user_type": "developer", "environment": "testing"}

    conversation = coze.conversations.create(name="带元数据的会话", meta_data=meta_data)

    print(f"会话ID: {conversation.id}")
    print(f"会话名称: {conversation.name}")
    print(f"元数据: {conversation.meta_data}")

    return conversation


def create_conversation_with_connector():
    """
    创建会话并指定渠道ID
    """
    print("\n=== 创建指定渠道的会话 ===")

    # 创建指定渠道ID的会话（1024为API渠道）
    conversation = coze.conversations.create(name="API渠道会话", connector_id="1024")

    print(f"会话ID: {conversation.id}")
    print(f"会话名称: {conversation.name}")
    print(f"渠道ID: {conversation.connector_id}")

    return conversation
