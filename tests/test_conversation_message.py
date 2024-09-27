import time
import unittest

from cozepy import COZE_CN_BASE_URL, Coze, Message
from tests.config import fixed_token_auth


@unittest.skip("not available in not cn")
def test_conversation_message():
    cli = Coze(auth=fixed_token_auth, base_url=COZE_CN_BASE_URL)

    # create conversation
    conversation = cli.conversations.create(
        messages=[
            Message.user_text_message("who are you?"),
            Message.assistant_text_message("i am your friend bob."),
        ]
    )
    assert conversation is not None

    # retrieve conversation
    conversation_retrieve = cli.conversations.retrieve(conversation_id=conversation.id)
    assert conversation.id == conversation_retrieve.id

    # create message
    user_input = Message.user_text_message("nice to meet you.")
    message = cli.conversations.messages.create(
        conversation_id=conversation.id,
        role=user_input.role,
        content=user_input.content,
        content_type=user_input.content_type,
    )
    assert message is not None
    assert message.id != ""

    time.sleep(1)

    # retrieve message
    message_retrieve = cli.conversations.messages.retrieve(conversation_id=conversation.id, message_id=message.id)
    assert message_retrieve is not None
    assert message.id == message_retrieve.id

    # list message
    message_list = cli.conversations.messages.list(conversation_id=conversation.id, message_id=message.id)
    assert len(message_list) > 2

    # update message
    cli.conversations.messages.update(
        conversation_id=conversation.id,
        message_id=message.id,
        content="wow, nice to meet you",
        content_type=message.content_type,
    )

    # delete message
    cli.conversations.messages.delete(
        conversation_id=conversation.id,
        message_id=message.id,
    )
