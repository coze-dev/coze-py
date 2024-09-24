import os

from cozepy import TokenAuth, Coze, COZE_CN_BASE_URL, Message, ChatIterator, Event
from cozepy.auth import _random_hex


def test_chat_v3_not_stream():
    token = os.getenv("COZE_TOKEN").strip()
    bot_id = os.getenv("COZE_BOT_ID_TRANSLATE").strip()

    auth = TokenAuth(token)
    cli = Coze(auth=auth, base_url=COZE_CN_BASE_URL)

    chat = cli.chat.chat_v3(
        bot_id=bot_id,
        user_id=_random_hex(10),
        additional_messages=[Message.user_text_message("Hi, how are you?")],
        stream=False,
    )
    assert chat is not None
    assert chat.id != ""


def test_chat_v3_stream():
    token = os.getenv("COZE_TOKEN").strip()
    bot_id = os.getenv("COZE_BOT_ID_TRANSLATE").strip()

    auth = TokenAuth(token)
    cli = Coze(auth=auth, base_url=COZE_CN_BASE_URL)

    chat_iter: ChatIterator = cli.chat.chat_v3(
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
