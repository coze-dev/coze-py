# Coze Python API SDK

[![PyPI version](https://img.shields.io/pypi/v/cozepy.svg)](https://pypi.org/project/cozepy/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/cozepy)
[![codecov](https://codecov.io/github/coze-dev/coze-py/graph/badge.svg?token=U6OKGQXF0E)](https://codecov.io/github/coze-dev/coze-py)

## Introduction

The Coze API SDK for Python is a versatile tool for integrating Coze's open APIs into
your projects.

- Supports all Coze open APIs and authentication APIs
- Supports both synchronous and asynchronous SDK calls
- Optimized for streaming apis, returning Stream and AsyncStream objects
- Optimized for list apis, returning Iterator Page objects
- Features a simple and user-friendly API design for ease of use

## Requirements

Python 3.7 or higher.

## Install

```shell
pip install cozepy
```

## Usage

### Examples

<table>
    <tr>
        <th>Module</th>
        <th>Example</th>
        <th>File</th>
    </tr>
    <tr>
        <td rowspan="5">Auth</td>
        <td>JWT OAuth</td>
        <td><a href="./examples/auth_oauth_jwt.py">examples/auth_oauth_jwt.py</a></td>
    </tr>
    <tr>
        <td>Web OAuth</td>
        <td><a href="./examples/auth_oauth_web.py">examples/auth_oauth_web.py</a></td>
    </tr>
    <tr>
        <td>PKCE OAuth</td>
        <td><a href="./examples/auth_oauth_pkce.py">examples/auth_oauth_pkce.py</a></td>
    </tr>
    <tr>
        <td>Device OAuth</td>
        <td><a href="./examples/auth_oauth_device.py">examples/auth_oauth_device.py</a></td>
    </tr>
    <tr>
        <td>Personal Access Token</td>
        <td><a href="./examples/auth_pat.py">examples/auth_pat.py</a></td>
    </tr>
    <tr>
        <td rowspan="4">Websockets</td>
        <td>Audio Speech by Websocket</td>
        <td><a href="./examples/websockets_audio_speech.py">examples/websockets_audio_speech.py</a></td>
    </tr>
    <tr>
        <td>Audio Transcription by Websocket</td>
        <td><a href="./examples/websockets_audio_transcriptions.py">examples/websockets_audio_transcriptions.py</a></td>
    </tr>
    <tr>
        <td>Audio Chat by Websocket</td>
        <td><a href="./examples/websockets_chat.py">examples/websockets_chat.py</a></td>
    </tr>
    <tr>
        <td>Audio Chat Realtime by Websocket</td>
        <td><a href="./examples/websockets_chat_realtime_gui.py">examples/websockets_chat_realtime_gui.py</a></td>
    </tr>
    <tr>
        <td rowspan="7">Bot Chat</td>
        <td>Bot Chat with Stream</td>
        <td><a href="./examples/chat_stream.py">examples/chat_stream.py</a></td>
    </tr>
    <tr>
        <td>Bot Chat without Stream</td>
        <td><a href="./examples/chat_no_stream.py">examples/chat_no_stream.py</a></td>
    </tr>
    <tr>
        <td>Bot Chat with Conversation</td>
        <td><a href="./examples/chat_conversation_stream.py">examples/chat_conversation_stream.py</a></td>
    </tr>
    <tr>
        <td>Bot Chat with Image</td>
        <td><a href="./examples/chat_multimode_stream.py">examples/chat_multimode_stream.py</a></td>
    </tr>
    <tr>
        <td>Bot Chat with Audio</td>
        <td><a href="./examples/chat_simple_audio.py">examples/chat_simple_audio.py</a></td>
    </tr>
    <tr>
        <td>Bot Chat with Audio One-One</td>
        <td><a href="./examples/chat_oneonone_audio.py">examples/chat_oneonone_audio.py</a></td>
    </tr>
    <tr>
        <td>Bot Chat With Local Plugin</td>
        <td><a href="./examples/chat_local_plugin.py">examples/chat_local_plugin.py</a></td>
    </tr>
    <tr>
        <td rowspan="5">Workflow Run & Chat</td>
        <td>Workflow Run with Stream</td>
        <td><a href="./examples/workflow_stream.py">examples/workflow_stream.py</a></td>
    </tr>
    <tr>
        <td>Workflow Run without Stream</td>
        <td><a href="./examples/workflow_no_stream.py">examples/workflow_no_stream.py</a></td>
    </tr>
    <tr>
        <td>Workflow Async Run & Fetch</td>
        <td><a href="./examples/workflow_async.py">examples/workflow_async.py</a></td>
    </tr>
    <tr>
        <td>Workflow Chat with Stream</td>
        <td><a href="./examples/workflow_chat_stream.py">examples/workflow_chat_stream.py</a></td>
    </tr>
    <tr>
        <td>Workflow chat with Image and Stream</td>
        <td><a href="./examples/workflow_chat_multimode_stream.py">examples/workflow_chat_multimode_stream.py</a></td>
    </tr>
    <tr>
        <td rowspan="2">Conversation</td>
        <td>Conversation</td>
        <td><a href="./examples/conversation.py">examples/conversation.py</a></td>
    </tr>
    <tr>
        <td>List Conversation</td>
        <td><a href="./examples/conversation_list.py">examples/conversation_list.py</a></td>
    </tr>
    <tr>
        <td rowspan="1">Dataset</td>
        <td>Create Dataset</td>
        <td><a href="./examples/dataset_create.py">examples/dataset_create.py</a></td>
    </tr>
    <tr>
        <td rowspan="1">Audio</td>
        <td>Audio Example by HTTP</td>
        <td><a href="./examples/audio.py">examples/audio.py</a></td>
    </tr>
    <tr>
        <td rowspan="1">Bot</td>
        <td>Publish Bot</td>
        <td><a href="./examples/bot_publish.py">examples/bot_publish.py</a></td>
    </tr>
    <tr>
        <td rowspan="1">File</td>
        <td>Upload File</td>
        <td><a href="./examples/files_upload.py">examples/files_upload.py</a></td>
    </tr>
    <tr>
        <td rowspan="1">template</td>
        <td>Duplicate Template</td>
        <td><a href="./examples/template_duplicate.py">examples/template_duplicate.py</a></td>
    </tr>
    <tr>
        <td rowspan="1">User</td>
        <td>Get Current User</td>
        <td><a href="./examples/users_me.py">examples/users_me.py</a></td>
    </tr>
    <tr>
        <td rowspan="1">Workspace</td>
        <td>List Workspaces</td>
        <td><a href="./examples/workspace.py">examples/workspace.py</a></td>
    </tr>
    <tr>
        <td rowspan="2">Variable</td>
        <td>Retrieve Variable</td>
        <td><a href="./examples/variable_retrieve.py">examples/variable_retrieve.py</a></td>
    </tr>
    <tr>
        <td>Update Variable</td>
        <td><a href="./examples/variable_update.py">examples/variable_update.py</a></td>
    </tr>
    <tr>
        <td rowspan="3">Other</td>
        <td>Timeout Config</td>
        <td><a href="./examples/timeout.py">examples/timeout.py</a></td>
    </tr>
    <tr>
        <td>Log Config</td>
        <td><a href="./examples/log.py">examples/log.py</a></td>
    </tr>
    <tr>
        <td>Exception Usage</td>
        <td><a href="./examples/exception.py">examples/exception.py</a></td>
    </tr>
</table>

### Initialize client

Firstly, you need to access https://www.coze.cn/open/oauth/pats (for the coze.com environment,
visit https://www.coze.com/open/oauth/pats).

Click to add a new token. After setting the
appropriate name, expiration time, and permissions, click OK to generate your personal
access token.

Please store it in a secure environment to prevent this personal access
token from being disclosed.

```python
import os

from cozepy import Coze, TokenAuth, COZE_CN_BASE_URL, AsyncCoze, AsyncTokenAuth

# Get an access_token through personal access token or oauth.
coze_api_token = os.getenv("COZE_API_TOKEN")
# The default access is api.coze.com, but if you need to access api.coze.cn,
# please use base_url to configure the api endpoint to access
coze_api_base = os.getenv("COZE_API_BASE") or COZE_CN_BASE_URL

# init coze with token and base_url
coze = Coze(auth=TokenAuth(coze_api_token), base_url=coze_api_base)
async_coze = AsyncCoze(auth=AsyncTokenAuth(coze_api_token), base_url=coze_api_base)
```

coze api access_token can also be generated via the OAuth App. For details, refer to:

- [Web OAuth](./examples/auth_oauth_web.py)
- [JWT OAuth](./examples/auth_oauth_jwt.py)
- [PKCE OAuth](./examples/auth_oauth_pkce.py)
- [Device OAuth](./examples/auth_oauth_device.py)

### Bot Chat

Create a bot instance in Coze, copy the last number from the web link as the bot's ID.

Call the coze.chat.stream method to create a chat. The create method is a streaming
chat and will return a Chat Iterator. Developers should iterate the iterator to get
chat event and handle them.

```python
import os

from cozepy import Coze, TokenAuth, Message, ChatEventType, COZE_CN_BASE_URL

# initialize client
coze_api_token = os.getenv("COZE_API_TOKEN")
coze_api_base = os.getenv("COZE_API_BASE") or COZE_CN_BASE_URL
coze = Coze(auth=TokenAuth(coze_api_token), base_url=coze_api_base)

# The return values of the streaming interface can be iterated immediately.
for event in coze.chat.stream(
        # id of bot
        bot_id='bot_id',
        # id of user, Note: The user_id here is specified by the developer, for example, it can be the
        # business id in the developer system, and does not include the internal attributes of coze.
        user_id='user_id',
        # user input
        additional_messages=[Message.build_user_question_text("How are you?")]
        # conversation id, for Chaining conversation context
        # conversation_id='<conversation_id>',
):
    if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
        print(event.message.content, end="")

    if event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
        print()
        print("token usage:", event.chat.usage.token_count)
```

### Workflow Chat

Coze also enables users to directly invoke the workflow.

```python

import os

from cozepy import TokenAuth, ChatEventType, Coze, COZE_CN_BASE_URL, Message

# Get the workflow id
workflow_id = os.getenv("COZE_WORKFLOW_ID") or "workflow id"
# Get the bot id
bot_id = os.getenv("COZE_BOT_ID")

# initialize client
coze_api_token = os.getenv("COZE_API_TOKEN")
coze_api_base = os.getenv("COZE_API_BASE") or COZE_CN_BASE_URL
coze = Coze(auth=TokenAuth(coze_api_token), base_url=coze_api_base)

conversation = coze.conversations.create()

# Call the coze.chat.stream method to create a chat. The create method is a streaming
# chat and will return a Chat Iterator. Developers should iterate the iterator to get
# chat event and handle them.
for event in coze.workflows.chat.stream(
        workflow_id=workflow_id,
        bot_id=bot_id,
        conversation_id=conversation.id,
        additional_messages=[
            Message.build_user_question_text("How are you?"),
        ],
):
    if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
        print(event.message.content, end="", flush=True)

    if event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
        print()
        print("token usage:", event.chat.usage.token_count)
```

### Audio Chat with websocket

```python
import asyncio
import os

from cozepy import (
    AsyncTokenAuth,
    COZE_CN_BASE_URL,
    AsyncCoze,
    AsyncWebsocketsChatClient,
    AsyncWebsocketsChatEventHandler,
    AudioFormat,
    ConversationAudioDeltaEvent,
    ConversationChatCompletedEvent,
    ConversationChatCreatedEvent,
    ConversationMessageDeltaEvent,
    InputAudioBufferAppendEvent,
)
from cozepy.log import log_info
from cozepy.util import write_pcm_to_wav_file


class AsyncWebsocketsChatEventHandlerSub(AsyncWebsocketsChatEventHandler):
    delta = []

    async def on_conversation_chat_created(self, cli: AsyncWebsocketsChatClient, event: ConversationChatCreatedEvent):
        log_info("[examples] asr completed, logid=%s", event.detail.logid)

    async def on_conversation_message_delta(self, cli: AsyncWebsocketsChatClient, event: ConversationMessageDeltaEvent):
        print("Received:", event.data.content)

    async def on_conversation_audio_delta(self, cli: AsyncWebsocketsChatClient, event: ConversationAudioDeltaEvent):
        self.delta.append(event.data.get_audio())

    async def on_conversation_chat_completed(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationChatCompletedEvent
    ):
        log_info("[examples] Saving audio data to output.wav")
        write_pcm_to_wav_file(b"".join(self.delta), "output.wav")


def wrap_coze_speech_to_iterator(coze: AsyncCoze, text: str):
    async def iterator():
        voices = await coze.audio.voices.list()
        content = await coze.audio.speech.create(
            input=text,
            voice_id=voices.items[0].voice_id,
            response_format=AudioFormat.WAV,
            sample_rate=24000,
        )
        for data in content._raw_response.iter_bytes(chunk_size=1024):
            yield data

    return iterator


async def main():
    coze_api_token = os.getenv("COZE_API_TOKEN")
    coze_api_base = os.getenv("COZE_API_BASE") or COZE_CN_BASE_URL
    coze = AsyncCoze(auth=AsyncTokenAuth(coze_api_token), base_url=coze_api_base)

    bot_id = os.getenv("COZE_BOT_ID")
    text = os.getenv("COZE_TEXT") or "How Are you?"

    # Initialize Audio
    speech_stream = wrap_coze_speech_to_iterator(coze, text)

    chat = coze.websockets.chat.create(
        bot_id=bot_id,
        on_event=AsyncWebsocketsChatEventHandlerSub(),
    )

    # Create and connect WebSocket client
    async with chat() as client:
        # Read and send audio data
        async for delta in speech_stream():
            await client.input_audio_buffer_append(
                InputAudioBufferAppendEvent.Data.model_validate(
                    {
                        "delta": delta,
                    }
                )
            )
        await client.input_audio_buffer_complete()
        await client.wait()


asyncio.run(main())
```

### LogID

The SDK support returning the logid of the request, which can be used to debug the request.
You can get the logid from the response of the request and submit it to the coze support team for further assistance.

```python
import os
from cozepy import Coze, TokenAuth

coze = Coze(auth=TokenAuth(os.getenv("COZE_API_TOKEN")))

bot = coze.bots.retrieve(bot_id='bot id')
print(bot.response.logid) # support for CozeModel

stream = coze.chat.stream(bot_id='bot id', user_id='user id')
print(stream.response.logid) # support for stream

workspaces = coze.workspaces.list()
print(workspaces.response.logid) # support for paged

messages = coze.chat.messages.list(conversation_id='conversation id', chat_id='chat id')
print(messages.response.logid) # support for list(simple list, not paged)
```


### Async usage

cozepy supports asynchronous calls through `httpx.AsyncClient`.

Just replace the `Coze` client with the `AsyncCoze` client to use all the asynchronous calls of the Coze OpenAPI.

```python
import os
import asyncio

from cozepy import AsyncTokenAuth, Message, AsyncCoze, COZE_CN_BASE_URL

# Get an access_token through personal access token or oauth.
coze_api_token = os.getenv("COZE_API_TOKEN")
# The default access is api.coze.com, but if you need to access api.coze.cn,
# please use base_url to configure the api endpoint to access
coze_api_base = os.getenv("COZE_API_BASE") or COZE_CN_BASE_URL

# init coze with token and base_url
coze = AsyncCoze(auth=AsyncTokenAuth(coze_api_token), base_url=coze_api_base)

async def main() -> None:
    chat = await coze.chat.create(
        bot_id='bot id',
        # id of user, Note: The user_id here is specified by the developer, for example, it can be the business id in the developer system, and does not include the internal attributes of coze.
        user_id='user id',
        additional_messages=[
            Message.build_user_question_text('how are you?'),
            Message.build_assistant_answer('I am fine, thank you.')
        ],
    )
    print('chat', chat)


asyncio.run(main())
```

### Streaming usage

Bot chat and workflow run support running in streaming mode.

chat streaming example:

```python
import os
from cozepy import Coze, TokenAuth, ChatEventType, Message

coze = Coze(auth=TokenAuth(os.getenv("COZE_API_TOKEN")))

stream = coze.chat.stream(
    bot_id='bot id',
    # id of user, Note: The user_id here is specified by the developer, for example, it can be the
    # business id in the developer system, and does not include the internal attributes of coze.
    user_id='user id',
    additional_messages=[
        Message.build_user_question_text('how are you?'),
        Message.build_assistant_answer('I am fine, thank you.')
    ],
)
for event in stream:
    if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
        print('got message delta:', event.message.content)
```

workflow streaming example:

```python
import os
from cozepy import Coze, TokenAuth, Stream, WorkflowEvent, WorkflowEventType

coze = Coze(auth=TokenAuth(os.getenv("COZE_API_TOKEN")))


def handle_workflow_iterator(stream: Stream[WorkflowEvent]):
    for event in stream:
        if event.event == WorkflowEventType.MESSAGE:
            print('got message', event.message)
        elif event.event == WorkflowEventType.ERROR:
            print('got error', event.error)
        elif event.event == WorkflowEventType.INTERRUPT:
            handle_workflow_iterator(coze.workflows.runs.resume(
                workflow_id='workflow id',
                event_id=event.interrupt.interrupt_data.event_id,
                resume_data='hey',
                interrupt_type=event.interrupt.interrupt_data.type,
            ))


handle_workflow_iterator(coze.workflows.runs.stream(
    workflow_id='workflow id',
    parameters={
        'input_key': 'input value',
    }
))
```

Asynchronous calls also support streaming mode:

```python
import os
import asyncio

from cozepy import AsyncTokenAuth, ChatEventType, Message, AsyncCoze

coze = AsyncCoze(auth=AsyncTokenAuth(os.getenv("COZE_API_TOKEN")))


async def main():
    stream = coze.chat.stream(
        bot_id='bot id',
        # id of user, Note: The user_id here is specified by the developer, for example, it can be the
        # business id in the developer system, and does not include the internal attributes of coze.
        user_id='user id',
        additional_messages=[
            Message.build_user_question_text('how are you?'),
            Message.build_assistant_answer('I am fine, thank you.')
        ],
    )
    async for event in stream:
        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            print('got message delta:', event.message.content)


asyncio.run(main())
```

### Paginator Iterator

The result returned by all list interfaces (both synchronous and asynchronous) is a paginator, which supports iteration.

Take the example of listing the bots in a space to explain the three ways to use the paginator iterator:

#### 1. Not using iterators

```python
import os
from cozepy import Coze, TokenAuth

coze = Coze(auth=TokenAuth(os.getenv("COZE_API_TOKEN")))

# open your workspace, browser url will be https://www.coze.com/space/<this is workspace id>/develop
# copy <this is workspace id> as workspace id
bots_page = coze.bots.list(space_id='workspace id', page_size=10)
bots = bots_page.items
total = bots_page.total
has_more = bots_page.has_more
```

#### 2. Iterate over the paginator, getting T

```python
import os
from cozepy import Coze, TokenAuth

coze = Coze(auth=TokenAuth(os.getenv("COZE_API_TOKEN")))

# open your workspace, browser url will be https://www.coze.com/space/<this is workspace id>/develop
# copy <this is workspace id> as workspace id
bots_page = coze.bots.list(space_id='workspace id', page_size=10)
for bot in bots_page:
    print('got bot:', bot)
```

Asynchronous methods also support:

```python
import os
import asyncio

from cozepy import AsyncTokenAuth, AsyncCoze

coze = AsyncCoze(auth=AsyncTokenAuth(os.getenv("COZE_API_TOKEN")))


async def main():
    # open your workspace, browser url will be https://www.coze.com/space/<this is workspace id>/develop
    # copy <this is workspace id> as workspace id
    bots_page = await coze.bots.list(space_id='workspace id', page_size=10)
    async for bot in bots_page:
        print('got bot:', bot)


asyncio.run(main())
```

#### 3. Iterate over the paginator iter_pages to get the next page paginator

```python
import os
from cozepy import Coze, TokenAuth

coze = Coze(auth=TokenAuth(os.getenv("COZE_API_TOKEN")))

# open your workspace, browser url will be https://www.coze.com/space/<this is workspace id>/develop
# copy <this is workspace id> as workspace id
bots_page = coze.bots.list(space_id='workspace id', page_size=10)
for page in bots_page.iter_pages():
    print('got page:', page.page_num)
    for bot in page.items:
        print('got bot:', bot)
```

Asynchronous methods also support:

```python
import asyncio
import os

from cozepy import AsyncTokenAuth, AsyncCoze

coze = AsyncCoze(auth=AsyncTokenAuth(os.getenv("COZE_API_TOKEN")))


async def main():
    # open your workspace, browser url will be https://www.coze.com/space/<this is workspace id>/develop
    # copy <this is workspace id> as workspace id
    bots_page = await coze.bots.list(space_id='workspace id', page_size=10)
    async for page in bots_page.iter_pages():
        print('got page:', page.page_num)
        for bot in page.items:
            print('got bot:', bot)


asyncio.run(main())
```

### Config

#### Log Config

coze support config logging level

```python
import logging

from cozepy import setup_logging

# open debug logging, default is warning
setup_logging(level=logging.DEBUG)
```

#### Timeout Config

Coze client is built on httpx, and supports passing a custom httpx.Client when initializing
Coze, and setting a timeout on the httpx.Client

```python
import os

import httpx

from cozepy import COZE_COM_BASE_URL, Coze, TokenAuth, SyncHTTPClient

# Coze client is built on httpx, and supports passing a custom httpx.Client when initializing
# Coze, and setting a timeout on the httpx.Client
http_client = SyncHTTPClient(timeout=httpx.Timeout(
    # 600s timeout on elsewhere
    timeout=600.0,
    # 5s timeout on connect
    connect=5.0
))

# Init the Coze client through the access_token and custom timeout http client.
coze = Coze(auth=TokenAuth(token=os.getenv("COZE_API_TOKEN")),
            base_url=COZE_COM_BASE_URL,
            http_client=http_client
            )
```
