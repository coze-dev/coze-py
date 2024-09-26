# coze-py

## Install

```shell
pip install cozepy
```

## Usage

### Auth

```python
from cozepy import Coze, TokenAuth, JWTAuth

# use pat or oauth token as auth
cli = Coze(auth=TokenAuth("your_token"))

# use application jwt auth flow as auth
cli = Coze(auth=JWTAuth("your_client_id", "your_private_key", "your_key_id"))
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

### Chat

```python
import time

from cozepy import Coze, TokenAuth, Event, ChatStatus, Message

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
    if event.event == Event.conversation_message_delta:
        print('got message delta:', event.messages.content)
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
from cozepy import Coze, TokenAuth, Event, WorkflowEventIterator

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
        if event.event == Event.message:
            print('got message', event.message)
        elif event.event == Event.error:
            print('got error', event.error)
        elif event.event == Event.interrupt:
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