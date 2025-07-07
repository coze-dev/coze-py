from typing import Any, AsyncIterator, Dict, List, Optional

from cozepy.chat import (
    ChatEvent,
    Message,
    _chat_stream_handler,
)
from cozepy.model import AsyncIteratorHTTPResponse, AsyncStream, IteratorHTTPResponse, Stream
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash


class WorkflowsChatClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def stream(
        self,
        *,
        workflow_id: str,
        additional_messages: Optional[List[Message]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        app_id: Optional[str] = None,
        bot_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        ext: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Stream[ChatEvent]:
        """
        Call the Chat API with streaming to send messages to a published Coze bot.

        docs en: https://www.coze.com/docs/developer_guides/workflow_chat
        docs zh: https://www.coze.cn/docs/developer_guides/workflow_chat

        :param workflow_id: The ID of the workflow that the API interacts with.
        :param additional_messages: Additional information for the conversation. You can pass the user's query for this
        conversation through this field. The array length is limited to 50, meaning up to 50 messages can be input.
        :param parameters: The parameters for the workflow.
        :param app_id: The ID of the app that the API interacts with.
        :param bot_id: The ID of the bot that the API interacts with.
        :param conversation_id: Indicate which conversation the chat is taking place in.
        :param ext: The extended information for the workflow.
        :return: iterator of ChatEvent
        """
        return self._create(
            workflow_id=workflow_id,
            additional_messages=additional_messages,
            parameters=parameters,
            app_id=app_id,
            bot_id=bot_id,
            conversation_id=conversation_id,
            ext=ext,
            **kwargs,
        )

    def _create(
        self,
        *,
        workflow_id: str,
        additional_messages: Optional[List[Message]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        app_id: Optional[str] = None,
        bot_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        ext: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Stream[ChatEvent]:
        url = f"{self._base_url}/v1/workflows/chat"
        body = remove_none_values(
            {
                "workflow_id": workflow_id,
                "additional_messages": [i.model_dump() for i in additional_messages] if additional_messages else [],
                "parameters": parameters,
                "app_id": app_id,
                "bot_id": bot_id,
                "conversation_id": conversation_id,
                "ext": ext,
            }
        )
        headers: Optional[dict] = kwargs.get("headers")
        response: IteratorHTTPResponse[str] = self._requester.request(
            "post",
            url,
            True,
            None,
            headers=headers,
            body=body,
        )
        return Stream(
            response._raw_response,
            response.data,
            fields=["event", "data"],
            handler=_chat_stream_handler,
        )


class AsyncWorkflowsChatClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def stream(
        self,
        *,
        workflow_id: str,
        additional_messages: Optional[List[Message]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        app_id: Optional[str] = None,
        bot_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        ext: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> AsyncIterator[ChatEvent]:
        """
        Call the Chat API with streaming to send messages to a published Coze bot.

        docs en: https://www.coze.com/docs/developer_guides/workflow_chat
        docs zh: https://www.coze.cn/docs/developer_guides/workflow_chat

        :param workflow_id: The ID of the workflow that the API interacts with.
        :param additional_messages: Additional information for the conversation. You can pass the user's query for this
        conversation through this field. The array length is limited to 50, meaning up to 50 messages can be input.
        :param parameters: The parameters for the workflow.
        :param app_id: The ID of the app that the API interacts with.
        :param bot_id: The ID of the bot that the API interacts with.
        :param conversation_id: Indicate which conversation the chat is taking place in.
        :param ext: The extended information for the workflow.
        :return: iterator of ChatEvent
        """
        async for item in await self._create(
            workflow_id=workflow_id,
            additional_messages=additional_messages,
            parameters=parameters,
            app_id=app_id,
            bot_id=bot_id,
            conversation_id=conversation_id,
            ext=ext,
            **kwargs,
        ):
            yield item

    async def _create(
        self,
        *,
        workflow_id: str,
        additional_messages: Optional[List[Message]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        app_id: Optional[str] = None,
        bot_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        ext: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> AsyncIterator[ChatEvent]:
        url = f"{self._base_url}/v1/workflows/chat"
        body = remove_none_values(
            {
                "workflow_id": workflow_id,
                "additional_messages": [i.model_dump() for i in additional_messages] if additional_messages else [],
                "parameters": parameters,
                "app_id": app_id,
                "bot_id": bot_id,
                "conversation_id": conversation_id,
                "ext": ext,
            }
        )
        headers: Optional[dict] = kwargs.get("headers")
        resp: AsyncIteratorHTTPResponse[str] = await self._requester.arequest(
            "post",
            url,
            True,
            None,
            headers=headers,
            body=body,
        )

        return AsyncStream(
            resp.data, fields=["event", "data"], handler=_chat_stream_handler, raw_response=resp._raw_response
        )
