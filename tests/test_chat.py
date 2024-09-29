import os

from cozepy import COZE_CN_BASE_URL, ChatEventType, Coze, Message
from cozepy.util import random_hex
from tests.config import fixed_token_auth


def test_chat_v3_not_stream():
    bot_id = os.getenv("COZE_BOT_ID_TRANSLATE").strip()

    cli = Coze(auth=fixed_token_auth, base_url=COZE_CN_BASE_URL)

    chat = cli.chat.create(
        bot_id=bot_id,
        user_id=random_hex(10),
        additional_messages=[Message.user_text_message("Hi, how are you?")],
    )
    assert chat is not None
    assert chat.id != ""

    # while True:
    #     chat = cli.chat.get(conversation_id=chat.conversation_id, chat_id=chat.id)
    #     if chat.status != ChatStatus.in_progress:
    #         break
    # messages = cli.chat.messages.list(conversation_id=chat.conversation_id, chat_id=chat.id)
    # print(messages)
    # assert len(messages) > 0


def test_chat_stream():
    bot_id = os.getenv("COZE_BOT_ID_TRANSLATE").strip()

    cli = Coze(auth=fixed_token_auth, base_url=COZE_CN_BASE_URL)

    chat_iter = cli.chat.stream(
        bot_id=bot_id,
        user_id=random_hex(10),
        additional_messages=[Message.user_text_message("Hi, how are you?")],
    )
    for item in chat_iter:
        assert item is not None
        assert item.event != ""
        if item.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            assert item.message.content != ""
