# Coze Python API SDK

[![PyPI version](https://img.shields.io/pypi/v/cozepy.svg)](https://pypi.org/project/cozepy/)
[![codecov](https://codecov.io/github/coze-dev/coze-py/graph/badge.svg?token=U6OKGQXF0E)](https://codecov.io/github/coze-dev/coze-py)

- Supports all Coze open APIs and authentication methods
- Supports both synchronous and asynchronous function calls
- Optimized for streaming interfaces, returning Stream and AsyncStream objects
- Features a simple and user-friendly API design for ease of use

## Requirements

Python 3.7 or higher.

## Install

```shell
pip install cozepy
```

## Usage

### Initialize the coze client

#### Fixed Auth Token

create Personal Auth Token at [扣子](https://www.coze.cn/open/oauth/pats)
or [Coze Platform](https://www.coze.com/open/oauth/pats)

and use `TokenAuth` to init Coze client.

```python
from cozepy import Coze, TokenAuth

# use pat or oauth token as auth
coze = Coze(auth=TokenAuth("your_token"))
```

#### JWT OAuth App

create JWT OAuth App at [扣子](https://www.coze.cn/open/oauth/apps)
or [Coze Platform](https://www.coze.com/open/oauth/apps)

```python
from cozepy import Coze, JWTAuth

# use application jwt auth flow as auth
coze = Coze(auth=JWTAuth("your_client_id", "your_private_key", "your_key_id"))
```

### Chat

```python
import time

from cozepy import Coze, TokenAuth, ChatEventType, ChatStatus, Message

coze = Coze(auth=TokenAuth("your_token"))

# no-stream chat
chat = coze.chat.create(
    bot_id='bot id',
    user_id='user id',
    additional_messages=[
        Message.user_text_message('how are you?'),
        Message.assistant_text_message('I am fine, thank you.')
    ],
)
start = int(time.time())
while chat.status == ChatStatus.IN_PROGRESS:
    if int(time.time()) - start > 120:
        # too long, cancel chat
        coze.chat.cancel(conversation_id=chat.conversation_id, chat_id=chat.chat_id)
        break

    time.sleep(1)
    chat = coze.chat.retrieve(conversation_id=chat.conversation_id, chat_id=chat.chat_id)

message_list = coze.chat.messages.list(conversation_id=chat.conversation_id, chat_id=chat.chat_id)
for message in message_list:
    print('got message:', message.content)

# stream chat
stream = coze.chat.stream(
    bot_id='bot id',
    user_id='user id',
    additional_messages=[
        Message.user_text_message('how are you?'),
        Message.assistant_text_message('I am fine, thank you.')
    ],
)
for event in stream:
    if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
        print('got message delta:', event.message.content)
```

### Bots

```python
from cozepy import Coze, TokenAuth

coze = Coze(auth=TokenAuth("your_token"))

# retrieve bot info
bot = coze.bots.retrieve(bot_id='bot id')

# list bot list
bots_page = coze.bots.list(space_id='space id', page_num=1)
bots = bots_page.items

# create bot
bot = coze.bots.create(
    space_id='space id',
    name='bot name',
    description='bot description',
)

# update bot info
coze.bots.update(
    bot_id='bot id',
    name='bot name',
    description='bot description',
)

# delete bot
bot = coze.bots.publish(bot_id='bot id')
```

### Conversations

```python
from cozepy import Coze, TokenAuth, Message, MessageContentType

coze = Coze(auth=TokenAuth("your_token"))

# create conversation
conversation = coze.conversations.create(
    messages=[
        Message.user_text_message('how are you?'),
        Message.assistant_text_message('I am fine, thank you.')
    ],
)

# retrieve conversation
conversation = coze.conversations.retrieve(conversation_id=conversation.id)

# create message
message = coze.conversations.messages.create(
    conversation_id=conversation.id,
    content='how are you?',
    content_type=MessageContentType.TEXT,
)

# retrieve message
message = coze.conversations.messages.retrieve(conversation_id=conversation.id, message_id=message.id)

# update message
coze.conversations.messages.update(
    conversation_id=conversation.id,
    message_id=message.id,
    content='hey, how are you?',
    content_type=MessageContentType.TEXT,
)

# delete message
coze.conversations.messages.delete(conversation_id=conversation.id, message_id=message.id)

# list messages
message_list = coze.conversations.messages.list(conversation_id=conversation.id)
```

### Files

```python
from cozepy import Coze, TokenAuth

coze = Coze(auth=TokenAuth("your_token"))

# upload file
file = coze.files.upload(file='/filepath')

# retrieve file info
coze.files.retrieve(file_id=file.id)
```

### Workflows

```python
from cozepy import Coze, TokenAuth, Stream, WorkflowEvent, WorkflowEventType

coze = Coze(auth=TokenAuth("your_token"))

# no-stream workflow run
result = coze.workflows.runs.create(
    workflow_id='workflow id',
    parameters={
        'input_key': 'input value',
    }
)


# stream workflow run
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

### Knowledge

```python
from cozepy import Coze, TokenAuth, DocumentBase, DocumentSourceInfo, DocumentChunkStrategy, DocumentUpdateRule

coze = Coze(auth=TokenAuth("your_token"))

# create knowledge documents by local_file
documents = coze.knowledge.documents.create(
    dataset_id='dataset id',
    document_bases=[
        DocumentBase(
            name='document name',
            source_info=DocumentSourceInfo.from_local_file('local file content')
        )
    ],
    chunk_strategy=DocumentChunkStrategy.auto()
)

# create knowledge documents by web_page
documents = coze.knowledge.documents.create(
    dataset_id='dataset id',
    document_bases=[
        DocumentBase(
            name='document name',
            source_info=DocumentSourceInfo.from_web_page('https://example.com')
        )
    ],
    chunk_strategy=DocumentChunkStrategy.auto()
)

# update knowledge document
coze.knowledge.documents.update(
    document_id='document id',
    document_name='name',
    update_rule=DocumentUpdateRule.no_auto_update()
)

# delete knowledge document
coze.knowledge.documents.delete(document_ids=['document id'])

# list knowledge documents
paged_documents = coze.knowledge.documents.list(
    dataset_id='dataset id',
    page_num=1,
    page_size=10
)
```

### OAuth App

#### Web OAuth App

```python
from cozepy import Coze, TokenAuth, WebOAuthApp

web_oauth_app = WebOAuthApp(
    client_id='client id',
    client_secret='client secret',
)

url = web_oauth_app.get_oauth_url(redirect_uri='http://127.0.0.1:8080', state='mock')

# open url

# Open the authorization link in your browser and authorize this OAuth App
# After authorization, you will be redirected to the redirect_uri with a code and state
# You can use the code to get the access token
code = 'mock code'

oauth_token = web_oauth_app.get_access_token(redirect_uri='http://127.0.0.1:8080', code=code)

# use the access token to init Coze client
coze = Coze(auth=TokenAuth(oauth_token.access_token))

# When the token expires, you can also refresh and re-obtain the token
oauth_token = web_oauth_app.refresh_access_token(oauth_token.refresh_token)
```

#### JWT OAuth App

```python
from cozepy import Coze, TokenAuth, JWTOAuthApp

jwt_oauth_app = JWTOAuthApp(
    client_id='client id',
    private_key='private key',
    public_key_id='public key id'
)

# The jwt process does not require any other operations, you can directly apply for a token
oauth_token = jwt_oauth_app.get_access_token(ttl=3600)

# And it does not support refresh. If you want to get a new token, you can call the get_access_token interface again.

# use the access token to init Coze client
coze = Coze(auth=TokenAuth(oauth_token.access_token))
```

#### PKCE OAuth App

```python
from cozepy import Coze, TokenAuth, PKCEOAuthApp

pkce_oauth_app = PKCEOAuthApp(
    client_id='client id',
)
code_verifier = 'mock code_verifier'
url = pkce_oauth_app.get_oauth_url(redirect_uri='http://127.0.0.1:8080', state='mock', code_verifier=code_verifier)

# open url

# Open the authorization link in your browser and authorize this OAuth App
# After authorization, you can exchange code_verifier for access token
code = 'mock code'

oauth_token = pkce_oauth_app.get_access_token(redirect_uri='http://127.0.0.1:8080', code=code,
                                              code_verifier=code_verifier)

# use the access token to init Coze client
coze = Coze(auth=TokenAuth(oauth_token.access_token))

# When the token expires, you can also refresh and re-obtain the token
oauth_token = pkce_oauth_app.refresh_access_token(oauth_token.refresh_token)
```

#### Device OAuth App

```python
from cozepy import Coze, TokenAuth, DeviceOAuthApp

device_oauth_app = DeviceOAuthApp(
    client_id='client id',
)

# First, you need to request the server to obtain the device code required in the device auth flow
device_code = device_oauth_app.get_device_code()

# open device_code.verification_url

# Open the authorization link in your browser and authorize this OAuth App
# After authorization, you can exchange the device code for an access token

oauth_token = device_oauth_app.get_access_token(device_code.device_code, poll=True)

# use the access token to init Coze client
coze = Coze(auth=TokenAuth(oauth_token.access_token))

# When the token expires, you can also refresh and re-obtain the token
oauth_token = device_oauth_app.refresh_access_token(oauth_token.refresh_token)
```

### Async usage

cozepy supports asynchronous calls through httpx.AsyncClient.

Just replace the `Coze` client with the `AsyncCoze` client to use all the asynchronous calls of the Coze OpenAPI.

```python
import asyncio

from cozepy import TokenAuth, Message, AsyncCoze

coze = AsyncCoze(auth=TokenAuth("your_token"))


async def main() -> None:
    chat = await coze.chat.create(
        bot_id='bot id',
        user_id='user id',
        additional_messages=[
            Message.user_text_message('how are you?'),
            Message.assistant_text_message('I am fine, thank you.')
        ],
    )
    print('chat', chat)


asyncio.run(main())
```

### Streaming usage

Bot chat and workflow run support running in streaming mode.

chat streaming example:

```python
from cozepy import Coze, TokenAuth, ChatEventType, Message

coze = Coze(auth=TokenAuth("your_token"))

stream = coze.chat.stream(
    bot_id='bot id',
    user_id='user id',
    additional_messages=[
        Message.user_text_message('how are you?'),
        Message.assistant_text_message('I am fine, thank you.')
    ],
)
for event in stream:
    if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
        print('got message delta:', event.message.content)
```

workflow streaming example:

```python
from cozepy import Coze, TokenAuth, Stream, WorkflowEvent, WorkflowEventType

coze = Coze(auth=TokenAuth("your_token"))


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
import asyncio

from cozepy import TokenAuth, ChatEventType, Message, AsyncCoze

coze = AsyncCoze(auth=TokenAuth("your_token"))


async def main():
    stream = coze.chat.stream(
        bot_id='bot id',
        user_id='user id',
        additional_messages=[
            Message.user_text_message('how are you?'),
            Message.assistant_text_message('I am fine, thank you.')
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
from cozepy import Coze, TokenAuth

coze = Coze(auth=TokenAuth("your_token"))

bots_page = coze.bots.list(space_id='space id', page_size=10)
bots = bots_page.items
total = bots_page.total
has_more = bots_page.has_more
```

#### 2. Iterate over the paginator, getting T

```python
from cozepy import Coze, TokenAuth

coze = Coze(auth=TokenAuth("your_token"))

bots_page = coze.bots.list(space_id='space id', page_size=10)
for bot in bots_page:
    print('got bot:', bot)
```

Asynchronous methods also support:

```python
import asyncio

from cozepy import TokenAuth, AsyncCoze

coze = AsyncCoze(auth=TokenAuth("your_token"))


async def main():
    bots_page = await coze.bots.list(space_id='space id', page_size=10)
    async for bot in bots_page:
        print('got bot:', bot)


asyncio.run(main())
```

#### 3. Iterate over the paginator iter_pages to get the next page paginator

```python
from cozepy import Coze, TokenAuth

coze = Coze(auth=TokenAuth("your_token"))

bots_page = coze.bots.list(space_id='space id', page_size=10)
for page in bots_page.iter_pages():
    print('got page:', page.page_num)
    for bot in page.items:
        print('got bot:', bot)
```

Asynchronous methods also support:

```python
import asyncio

from cozepy import TokenAuth, AsyncCoze

coze = AsyncCoze(auth=TokenAuth("your_token"))


async def main():
    bots_page = await coze.bots.list(space_id='space id', page_size=10)
    async for page in bots_page.iter_pages():
        print('got page:', page.page_num)
        for bot in page.items:
            print('got bot:', bot)


asyncio.run(main())
```
