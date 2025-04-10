"""
This use case teaches you how to use local plugin.
"""

import json
import os
from typing import List, Optional

from cozepy import (  # noqa
    COZE_CN_BASE_URL,
    ChatEvent,
    ChatEventType,
    ChatStatus,
    Coze,
    DeviceOAuthApp,
    Message,
    MessageContentType,
    Stream,
    TokenAuth,
    ToolOutput,
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
# Create a bot instance in Coze, copy the last number from the web link as the bot's ID.
bot_id = os.environ.get("BOT_ID")
# The user id identifies the identity of a user. Developers can use a custom business ID
# or a random string.
user_id = "user id"


# These two functions are mock implementations.
class LocalPluginMocker(object):
    @staticmethod
    def get_schedule():
        return "I have two interviews in the afternoon."

    @staticmethod
    def screenshot():
        return "The background of my screen is a little dog running on the beach."

    @staticmethod
    def get_function(name: str):
        return {
            "get_schedule": LocalPluginMocker.get_schedule,
            "screenshot": LocalPluginMocker.screenshot,
        }[name]


# `handle_stream` is used to handle events. When the `CONVERSATION_CHAT_REQUIRES_ACTION` event is received,
# the `submit_tool_outputs` method needs to be called to submit the running result.
def handle_stream(stream: Stream[ChatEvent]):
    for event in stream:
        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            print(event.message.content, end="", flush=True)

        if event.event == ChatEventType.CONVERSATION_CHAT_REQUIRES_ACTION:
            if not event.chat.required_action or not event.chat.required_action.submit_tool_outputs:
                continue
            tool_calls = event.chat.required_action.submit_tool_outputs.tool_calls
            tool_outputs: List[ToolOutput] = []
            for tool_call in tool_calls:
                print(f"function call: {tool_call.function.name} {tool_call.function.arguments}")
                local_function = LocalPluginMocker.get_function(tool_call.function.name)
                output = json.dumps({"output": local_function()})
                tool_outputs.append(ToolOutput(tool_call_id=tool_call.id, output=output))

            handle_stream(
                coze.chat.submit_tool_outputs(
                    conversation_id=event.chat.conversation_id,
                    chat_id=event.chat.id,
                    tool_outputs=tool_outputs,
                    stream=True,
                )
            )

        if event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
            print()
            print("token usage:", event.chat.usage.token_count)


# The intelligent entity will call LocalPluginMocker.get_schedule to obtain the schedule.
# get_schedule is just a mock method.
handle_stream(
    coze.chat.stream(
        bot_id=bot_id,
        user_id=user_id,
        additional_messages=[
            Message.build_user_question_text("What do I have to do in the afternoon?"),
        ],
    )
)

# The intelligent entity will obtain a screenshot through LocalPluginMocker.screenshot.
handle_stream(
    coze.chat.stream(
        bot_id=bot_id,
        user_id=user_id,
        additional_messages=[
            Message.build_user_question_text("What's on my screen?"),
        ],
    )
)
