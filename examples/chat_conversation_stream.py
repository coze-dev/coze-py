"""
This example is about how to use conversation to pass context
"""

import os
from typing import Callable, Optional

from cozepy import COZE_CN_BASE_URL, ChatEventType, Coze, DeviceOAuthApp, Message, TokenAuth


def build_translate_chinese_to_english_context(coze: Coze, bot_id: str) -> Callable[[str], str]:
    conversation = coze.conversations.create(
        messages=[
            Message.build_user_question_text("You need to translate the Chinese to English."),
            Message.build_assistant_answer("OK."),
        ]
    )

    # Call chat.stream and parse the return value to get the translation result.
    def translate_on_translate_chinese_to_english_context(text: str) -> str:
        for event in coze.chat.stream(
            bot_id=bot_id,
            user_id="fake user id",
            additional_messages=[
                Message.build_user_question_text(text),
            ],
            conversation_id=conversation.id,
        ):
            if event.event == ChatEventType.CONVERSATION_MESSAGE_COMPLETED:
                return event.message.content

    return translate_on_translate_chinese_to_english_context


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
# Create a bot instance in Coze, copy the last number from the web link as the bot's ID.
bot_id = os.getenv("COZE_BOT_ID") or "bot id"

translate_func = build_translate_chinese_to_english_context(coze, bot_id)

print("translate:", translate_func("地球与宇宙"))
