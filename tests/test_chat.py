import os

from cozepy import Coze, COZE_CN_BASE_URL, Message
from cozepy.auth import _random_hex
from cozepy.chat.v3 import ChatIterator, Event
from tests.config import fixed_token_auth


def test_chat_v3_not_stream():
    bot_id = os.getenv("COZE_BOT_ID_TRANSLATE").strip()

    cli = Coze(auth=fixed_token_auth, base_url=COZE_CN_BASE_URL)

    chat = cli.chat.v3.create(
        bot_id=bot_id,
        user_id=_random_hex(10),
        additional_messages=[Message.user_text_message("Hi, how are you?")],
        stream=False,
    )
    assert chat is not None
    assert chat.id != ""

    # while True:
    #     chat = cli.chat.get_v3(conversation_id=chat.conversation_id, chat_id=chat.id)
    #     if chat.status != ChatStatus.in_progress:
    #         break
    # messages = cli.chat.list_message_v3(conversation_id=chat.conversation_id, chat_id=chat.id)
    # print(messages)
    # assert len(messages) > 0


def test_chat_v3_stream():
    bot_id = os.getenv("COZE_BOT_ID_TRANSLATE").strip()

    cli = Coze(auth=fixed_token_auth, base_url=COZE_CN_BASE_URL)

    chat_iter: ChatIterator = cli.chat.v3.create(
        bot_id=bot_id,
        user_id=_random_hex(10),
        additional_messages=[Message.user_text_message("Hi, how are you?")],
        stream=True,
    )
    for item in chat_iter:
        assert item is not None
        assert item.event != ""
        if item.event == Event.conversation_message_delta:
            assert item.message.content != ""
