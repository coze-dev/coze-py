import json
from enum import Enum
from typing import Dict, List, Iterator, Tuple, Union

from .auth import Auth
from .model import Message, Chat, MessageResponse, CozeModel
from .request import Requester


class Event(str, Enum):
    # Event for creating a conversation, indicating the start of the conversation.
    # 创建对话的事件，表示对话开始。
    conversation_chat_created = "conversation.chat.created"

    # The server is processing the conversation.
    # 服务端正在处理对话。
    conversation_chat_in_progress = "conversation.chat.in_progress"

    # Incremental message, usually an incremental message when type=answer.
    # 增量消息，通常是 type=answer 时的增量消息。
    conversation_message_delta = "conversation.message.delta"

    # The message has been completely replied to. At this point, the streaming package contains the spliced results of all message.delta, and each message is in a completed state.
    # message 已回复完成。此时流式包中带有所有 message.delta 的拼接结果，且每个消息均为 completed 状态。
    conversation_message_completed = "conversation.message.completed"

    # The conversation is completed.
    # 对话完成。
    conversation_chat_completed = "conversation.chat.completed"

    # This event is used to mark a failed conversation.
    # 此事件用于标识对话失败。
    conversation_chat_failed = "conversation.chat.failed"

    # The conversation is interrupted and requires the user to report the execution results of the tool.
    # 对话中断，需要使用方上报工具的执行结果。
    conversation_chat_requires_action = "conversation.chat.requires_action"

    # Error events during the streaming response process. For detailed explanations of code and msg, please refer to Error codes.
    # 流式响应过程中的错误事件。关于 code 和 msg 的详细说明，可参考错误码。
    error = "error"

    # The streaming response for this session ended normally.
    # 本次会话的流式返回正常结束。
    done = "done"


class ChatEvent(CozeModel):
    event: Event
    chat: Chat = None
    message: MessageResponse = None


class ChatIterator(object):
    def __init__(self, iters: Iterator[bytes]):
        self._iters = iters

    def __iter__(self):
        return self

    def __next__(self) -> ChatEvent:
        event = ""
        data = ""
        line = ""
        times = 0

        while times < 2:
            line = next(self._iters).decode("utf-8")
            if line == "":
                continue
            elif line.startswith("event:"):
                if event == "":
                    event = line[6:]
                else:
                    raise Exception(f"invalid event: {line}")
            elif line.startswith("data:"):
                if data == "":
                    data = line[5:]
                else:
                    raise Exception(f"invalid event: {line}")
            else:
                raise Exception(f"invalid event: {line}")

            times += 1

        if event == Event.done:
            raise StopIteration
        elif event == Event.error:
            raise Exception(f"error event: {line}")
        elif event in [Event.conversation_message_delta, Event.conversation_message_completed]:
            return ChatEvent(event=event, message=MessageResponse.model_validate(json.loads(data)))
        elif event in [
            Event.conversation_chat_created,
            Event.conversation_chat_in_progress,
            Event.conversation_chat_completed,
            Event.conversation_chat_failed,
            Event.conversation_chat_requires_action,
        ]:
            return ChatEvent(event=event, chat=Chat.model_validate(json.loads(data)))
        else:
            raise Exception(f"unknown event: {line}")


class ChatClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester

    def chat_v3(
        self,
        *,
        bot_id: str,
        user_id: str,
        additional_messages: List[Message] = None,
        stream: bool = False,
        custom_variables: Dict[str, str] = None,
        auto_save_history: bool = True,
        meta_data: Dict[str, str] = None,
        conversation_id: str = None,
    ) -> Union[Chat, ChatIterator]:
        """
        Create a conversation.
        Conversation is an interaction between a bot and a user, including one or more messages.
        """
        url = f"{self._base_url}/v3/chat"
        body = {
            "bot_id": bot_id,
            "user_id": user_id,
            "additional_messages": [i.model_dump() for i in additional_messages] if additional_messages else [],
            "stream": stream,
            "custom_variables": custom_variables,
            "auto_save_history": auto_save_history,
            "conversation_id": conversation_id if conversation_id else None,
            "meta_data": meta_data,
        }
        if not stream:
            return self._requester.request("post", url, Chat, body=body, stream=stream)

        return ChatIterator(self._requester.request("post", url, Chat, body=body, stream=stream))
