"""
This use case teaches you how to use localplugin.
"""

import json
import os
from typing import List

from cozepy import COZE_COM_BASE_URL, ChatEvent, Stream, ToolOutput

# Get an access_token through personal access token or oauth.
coze_api_token = os.environ.get("COZE_API_TOKEN")
# The default access is api.coze.com, but if you need to access api.coze.cn,
# please use base_url to configure the api endpoint to access
coze_api_base = os.environ.get("COZE_API_BASE", COZE_COM_BASE_URL)

from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType, ChatEventType  # noqa

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

# Create a bot instance in Coze, copy the last number from the web link as the bot's ID.
bot_id = os.environ.get("BOT_ID")
# The user id identifies the identity of a user. Developers can use a custom business ID
# or a random string.
user_id = "user id"


# These two functions are mock implementations.
class MyFunction(object):
    def get_schedule(cls):
        return "I have two interviews in the afternoon."

    def screenshot(cls):
        return "The background of my screen is a little dog running on the beach."


# `handle_stream` is used to handle events. When the `CONVERSATION_CHAT_REQUIRES_ACTION` event is received,
# the `submit_tool_outputs` method needs to be called to submit the running result.
def handle_stream(stream: Stream[ChatEvent]):
    for event in stream:
        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            print(event.message.content, end="", flush=True)

        if event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
            print()
            print("token usage:", event.chat.usage.token_count)
        if event.event == ChatEventType.CONVERSATION_CHAT_REQUIRES_ACTION:
            if event.chat.required_action.submit_tool_outputs:
                tool_calls = event.chat.required_action.submit_tool_outputs.tool_calls
                tool_outputs: List[ToolOutput] = []
                for tool_call in tool_calls:
                    print(f"function call: {tool_call.function.name} {tool_call.function.arguments}")
                    myfunction = MyFunction()
                    fn = myfunction.__getattribute__(tool_call.function.name)
                    output = json.dumps({"output": fn()})
                    tool_outputs.append(ToolOutput(tool_call_id=tool_call.id, output=output))

                new_stream = coze.chat.submit_tool_outputs(
                    conversation_id=event.chat.conversation_id,
                    chat_id=event.chat.id,
                    tool_outputs=tool_outputs,
                    stream=True,
                )
                handle_stream(new_stream)


# The intelligent entity will call MyFunction.get_schedule to obtain the schedule.
# get_schedule is just a mock method.
stream = coze.chat.stream(
    bot_id=bot_id,
    user_id=user_id,
    additional_messages=[
        Message.build_user_question_text("What do I have to do in the afternoon?"),
    ],
)

handle_stream(stream)

# The intelligent entity will obtain a screenshot through MyFunction.screenshot.
stream = coze.chat.stream(
    bot_id=bot_id,
    user_id=user_id,
    additional_messages=[
        Message.build_user_question_text("What's on my screen?"),
    ],
)

handle_stream(stream)
