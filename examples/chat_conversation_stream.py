"""
This example is about how to use conversation to pass context
"""

import os
from typing import Callable

from cozepy import COZE_COM_BASE_URL, ChatEventType, ChatStatus, Coze, Message, MessageContentType, TokenAuth  # noqa


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


if __name__ == "__main__":
    # Get an access_token through personal access token or oauth.
    coze_api_token = os.getenv("COZE_API_TOKEN")
    # The default access is api.coze.com, but if you need to access api.coze.cn,
    # please use base_url to configure the api endpoint to access
    coze_api_base = os.getenv("COZE_API_BASE") or COZE_COM_BASE_URL
    # Init the Coze client through the access_token.
    coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)
    # Create a bot instance in Coze, copy the last number from the web link as the bot's ID.
    bot_id = os.getenv("COZE_BOT_ID") or "bot id"

    translate_func = build_translate_chinese_to_english_context(coze, bot_id)

    print("translate:", translate_func("地球与宇宙"))
