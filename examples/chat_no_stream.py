"""
This example describes how to use the chat interface to initiate conversations,
poll the status of the conversation, and obtain the messages after the conversation is completed.
"""

import os
import time

from cozepy import COZE_COM_BASE_URL

# Get an access_token through personal access token or oauth.
coze_api_token = os.getenv("COZE_API_TOKEN")
# The default access is api.coze.com, but if you need to access api.coze.cn,
# please use base_url to configure the api endpoint to access
coze_api_base = os.getenv("COZE_API_BASE") or COZE_COM_BASE_URL

from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType  # noqa

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

# Create a bot instance in Coze, copy the last number from the web link as the bot's ID.
bot_id = os.getenv("COZE_BOT_ID") or "bot id"
# The user id identifies the identity of a user. Developers can use a custom business ID
# or a random string.
user_id = "user id"

if os.getenv("RUN_STEP_BY_STEP"):
    # Call the coze.chat.create method to create a chat. The create method is a non-streaming
    # chat and will return a Chat class. Developers should periodically check the status of the
    # chat and handle them separately according to different states.
    chat = coze.chat.create(
        bot_id=bot_id,
        user_id=user_id,
        additional_messages=[
            Message.build_user_question_text("Who are you?"),
            Message.build_assistant_answer("I am Bot by Coze."),
            Message.build_user_question_text("What about you?"),
        ],
    )

    # Assume the development allows at most one chat to run for 10 minutes. If it exceeds 10
    # minutes, the chat will be cancelled.
    # And when the chat status is not completed, poll the status of the chat once every second.
    # After the chat is completed, retrieve all messages in the chat.
    start = int(time.time())
    timeout = 600
    while chat.status == ChatStatus.IN_PROGRESS:
        if int(time.time()) - start > timeout:
            # too long, cancel chat
            coze.chat.cancel(conversation_id=chat.conversation_id, chat_id=chat.id)
            break

        time.sleep(1)
        # Fetch the latest data through the retrieve interface
        chat = coze.chat.retrieve(conversation_id=chat.conversation_id, chat_id=chat.id)

    # When the chat status becomes completed, all messages under this chat can be retrieved through the list messages interface.
    messages = coze.chat.messages.list(conversation_id=chat.conversation_id, chat_id=chat.id)
    for message in messages:
        print(f"role={message.role}, content={message.content}")
else:
    # To simplify the call, the SDK provides a wrapped function to complete non-streaming chat,
    # polling, and obtaining the messages of the chat. Developers can use create_and_poll to
    # simplify the process.
    chat_poll = coze.chat.create_and_poll(
        bot_id=bot_id,
        user_id=user_id,
        additional_messages=[
            Message.build_user_question_text("Who are you?"),
            Message.build_assistant_answer("I am Bot by Coze."),
            Message.build_user_question_text("What about you?"),
        ],
    )
    for message in chat_poll.messages:
        print(message.content, end="", flush=True)

    if chat_poll.chat.status == ChatStatus.COMPLETED:
        print()
        print("token usage:", chat_poll.chat.usage.token_count)
