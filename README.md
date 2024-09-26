# coze-py

## Install

```shell
pip install cozepy
```

## Usage

### Auth

#### Personal Auth Token

create Personal Auth Token at [扣子](https://www.coze.cn/open/oauth/pats) or [Coze Platform](https://www.coze.com/open/oauth/pats)

and user `TokenAuth` to init Coze client.

```python
from cozepy import Coze, TokenAuth

# use pat or oauth token as auth
cli = Coze(auth=TokenAuth("your_token"))
```

#### JWT OAuth App

create JWT OAuth App at [扣子](https://www.coze.cn/open/oauth/apps) or [Coze Platform](https://www.coze.com/open/oauth/apps)

```python
from cozepy import Coze, JWTAuth

# use application jwt auth flow as auth
cli = Coze(auth=JWTAuth("your_client_id", "your_private_key", "your_key_id"))
```

### Chat

```python
import time

from cozepy import Coze, TokenAuth, ChatEventType, ChatStatus, Message

cli = Coze(auth=TokenAuth("your_token"))

# no-stream chat
chat = cli.chat.create(
    bot_id='bot id',
    user_id='user id',
    additional_messages=[
        Message.user_text_message('how are you?'),
        Message.assistant_text_message('I am fine, thank you.')
    ],
)
start = int(time.time())
while chat.status == ChatStatus.in_progress:
    if int(time.time()) > 120:
        # too long, cancel chat
        cli.chat.cancel(conversation_id=chat.conversation_id, chat_id=chat.chat_id)
        break

    time.sleep(1)
    chat = cli.chat.retrieve(conversation_id=chat.conversation_id, chat_id=chat.chat_id)

message_list = cli.chat.messages.list(conversation_id=chat.conversation_id, chat_id=chat.chat_id)
for message in message_list:
    print('got message:', message.content)

# stream chat
chat_iterator = cli.chat.stream(
    bot_id='bot id',
    user_id='user id',
    additional_messages=[
        Message.user_text_message('how are you?'),
        Message.assistant_text_message('I am fine, thank you.')
    ],
)
for event in chat_iterator:
    if event.event == ChatEventType.conversation_message_delta:
        print('got message delta:', event.messages.content)
```

### Bots

```python
from cozepy import Coze, TokenAuth

cli = Coze(auth=TokenAuth("your_token"))

# retrieve bot info
bot = cli.bots.retrieve(bot_id='bot id')

# list bot list
bots_page = cli.bots.list(space_id='space id', page_num=1)
bots = bots_page.items

# create bot
bot = cli.bots.create(
    space_id='space id',
    name='bot name',
    description='bot description',
)

# update bot info
cli.bots.update(
    bot_id='bot id',
    name='bot name',
    description='bot description',
)

# delete bot
bot = cli.bots.publish(bot_id='bot id')
```

### Conversations

```python
from cozepy import Coze, TokenAuth, Message, MessageContentType

cli = Coze(auth=TokenAuth("your_token"))

# create conversation
conversation = cli.conversations.create(
    messages=[
        Message.user_text_message('how are you?'),
        Message.assistant_text_message('I am fine, thank you.')
    ],
)

# retrieve conversation
conversation = cli.conversations.retrieve(conversation_id=conversation.id)

# create message
message = cli.conversations.messages.create(
    conversation_id=conversation.id,
    content='how are you?',
    content_type=MessageContentType.text,
)

# retrieve message
message = cli.conversations.messages.retrieve(conversation_id=conversation.id, message_id=message.id)

# update message
cli.conversations.messages.update(
    conversation_id=conversation.id,
    message_id=message.id,
    content='hey, how are you?',
    content_type=MessageContentType.text,
)

# delete message
cli.conversations.messages.delete(conversation_id=conversation.id, message_id=message.id)

# list messages
message_list = cli.conversations.messages.list(conversation_id=conversation.id)
```

### Files

```python
from cozepy import Coze, TokenAuth

cli = Coze(auth=TokenAuth("your_token"))

# upload file
file = cli.files.upload(file='/filepath')

# retrieve file info
cli.files.retrieve(file_id=file.id)
```

### Workflows

```python
from cozepy import Coze, TokenAuth, WorkflowEventType, WorkflowEventIterator

cli = Coze(auth=TokenAuth("your_token"))

# no-stream workflow run
result = cli.workflows.runs.create(
    workflow_id='workflow id',
    parameters={
        'input_key': 'input value',
    }
)


# stream workflow run
def handle_workflow_iterator(iterator: WorkflowEventIterator):
    for event in iterator:
        if event.event == WorkflowEventType.message:
            print('got message', event.message)
        elif event.event == WorkflowEventType.error:
            print('got error', event.error)
        elif event.event == WorkflowEventType.interrupt:
            handle_workflow_iterator(cli.workflows.runs.resume(
                workflow_id='workflow id',
                event_id=event.interrupt.interrupt_data.event_id,
                resume_data='hey',
                interrupt_type=event.interrupt.interrupt_data.type,
            ))


handle_workflow_iterator(cli.workflows.runs.stream(
    workflow_id='workflow id',
    parameters={
        'input_key': 'input value',
    }
))
```