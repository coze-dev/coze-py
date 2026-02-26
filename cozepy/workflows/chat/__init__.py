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
        执行对话流

        在智能体中执行资源库中的对话流 workflow_id 必选 必选 app_id 不传 必选 bot_id 执行已发布的对话流。 接口说明 对话流是基于对话场景的特殊工作流，专门用于处理对话类请求。对话流通过对话的方式和用户交互，并完成复杂的业务逻辑。在应用中添加对话流，将对话中的用户指令拆分为一个个步骤节点，并为其设计用户界面，你可以搭建出适用于移动端或网页端的对话式 AI 应用，实现自动化、智能化的对话流程。关于对话流的详细说明可参考 工作流与对话流 。 此接口为流式响应模式，允许客户端在接收到完整的数据流之前就开始处理数据，例如在对话界面实时展示回复内容，减少客户端等待模型完整回复的时间。 此接口支持包括问答节点、输入节点等可能导致对话中断的节点，对话中断时只需再次调用对话流，在 additional_messages 中指定输入内容，即可继续对话。 此接口可用于调用空间资源库中的对话流，或扣子应用中的对话流。调用这两种对话流时，入参不同： 限制说明 通过 API 方式执行对话流前，应确认此对话流已发布，执行从未发布过的对话流时会返回错误码 4200。如果是扣子应用中的对话流，应先发布扣子应用为 API 服务；如果是空间资源库中的对话流，应先在资源库中发布对话流。 此接口暂不支持异步运行。 入参 不传 conversation_id 可选 必选 不传 可选 如果对话流的输入中包含文件、图片等多模态内容，需要先上传多模态内容以获取文件 ID 或 URL 地址，再将其作为对话流的输入。上传方式包括： 调用 上传文件 API，获取文件 ID，将此 ID 作为对话流的输入。 上传到第三方存储工具中，并获取一个公开可访问的 URL 地址，将此 URL 作为对话流的输入。 调用接口后，你可以从响应的 Done 事件中获得 debug_url，访问链接即可通过可视化界面查看对话流的试运行过程，其中包含每个执行节点的输入输出等详细信息，帮助你在线调试或排障。debug_url 的访问有效期为 7 天，过期后将无法访问。 在扣子应用中执行资源库中的对话流 扣子应用中的对话流 必选 必选 可选

        :param workflow_id: required 待执行的对话流 ID，此对话流应已发布
        :param additional_messages: required 对话中用户问题和历史消息
        :param parameters: required 设置对话流输入参数中的自定义参数 (map[String]any)
        :param app_id: 需要关联的扣子应用 ID
        :param bot_id: 需要关联的智能体 ID
        :param conversation_id: 对话流对应的会话 ID
        :param ext: 用于指定一些额外的字段，例如经纬度、用户ID等
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
        """
        执行对话流

        可选 入参 在智能体中执行资源库中的对话流 bot_id 可选 必选 必选 必选 不传 执行已发布的对话流。 接口说明 对话流是基于对话场景的特殊工作流，专门用于处理对话类请求。对话流通过对话的方式和用户交互，并完成复杂的业务逻辑。在应用中添加对话流，将对话中的用户指令拆分为一个个步骤节点，并为其设计用户界面，你可以搭建出适用于移动端或网页端的对话式 AI 应用，实现自动化、智能化的对话流程。关于对话流的详细说明可参考 工作流与对话流 。 此接口为流式响应模式，允许客户端在接收到完整的数据流之前就开始处理数据，例如在对话界面实时展示回复内容，减少客户端等待模型完整回复的时间。 此接口支持包括问答节点、输入节点等可能导致对话中断的节点，对话中断时只需再次调用对话流，在 additional_messages 中指定输入内容，即可继续对话。 此接口可用于调用空间资源库中的对话流，或扣子应用中的对话流。调用这两种对话流时，入参不同： 限制说明 通过 API 方式执行对话流前，应确认此对话流已发布，执行从未发布过的对话流时会返回错误码 4200。如果是扣子应用中的对话流，应先发布扣子应用为 API 服务；如果是空间资源库中的对话流，应先在资源库中发布对话流。 此接口暂不支持异步运行。 如果对话流的输入中包含文件、图片等多模态内容，需要先上传多模态内容以获取文件 ID 或 URL 地址，再将其作为对话流的输入。上传方式包括： 调用 上传文件 API，获取文件 ID，将此 ID 作为对话流的输入。 上传到第三方存储工具中，并获取一个公开可访问的 URL 地址，将此 URL 作为对话流的输入。 调用接口后，你可以从响应的 Done 事件中获得 debug_url，访问链接即可通过可视化界面查看对话流的试运行过程，其中包含每个执行节点的输入输出等详细信息，帮助你在线调试或排障。debug_url 的访问有效期为 7 天，过期后将无法访问。 在扣子应用中执行资源库中的对话流 扣子应用中的对话流 workflow_id 不传 必选 必选 app_id 必选 不传 conversation_id 可选

        :param workflow_id: required 待执行的对话流 ID，此对话流应已发布
        :param additional_messages: required 对话中用户问题和历史消息
        :param parameters: required 设置对话流输入参数中的自定义参数 (map[String]any)
        :param app_id: 需要关联的扣子应用 ID
        :param bot_id: 需要关联的智能体 ID
        :param conversation_id: 对话流对应的会话 ID
        :param ext: 用于指定一些额外的字段，例如经纬度、用户ID等
        """
        url = f"{self._base_url}/v1/workflows/chat"
        headers: Optional[dict] = kwargs.get("headers")
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
        response: IteratorHTTPResponse[str] = self._requester.request(
            "post",
            url,
            True,
            cast=None,
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
        执行对话流

        必选 必选 conversation_id 执行已发布的对话流。 接口说明 对话流是基于对话场景的特殊工作流，专门用于处理对话类请求。对话流通过对话的方式和用户交互，并完成复杂的业务逻辑。在应用中添加对话流，将对话中的用户指令拆分为一个个步骤节点，并为其设计用户界面，你可以搭建出适用于移动端或网页端的对话式 AI 应用，实现自动化、智能化的对话流程。关于对话流的详细说明可参考 工作流与对话流 。 此接口为流式响应模式，允许客户端在接收到完整的数据流之前就开始处理数据，例如在对话界面实时展示回复内容，减少客户端等待模型完整回复的时间。 此接口支持包括问答节点、输入节点等可能导致对话中断的节点，对话中断时只需再次调用对话流，在 additional_messages 中指定输入内容，即可继续对话。 此接口可用于调用空间资源库中的对话流，或扣子应用中的对话流。调用这两种对话流时，入参不同： 限制说明 通过 API 方式执行对话流前，应确认此对话流已发布，执行从未发布过的对话流时会返回错误码 4200。如果是扣子应用中的对话流，应先发布扣子应用为 API 服务；如果是空间资源库中的对话流，应先在资源库中发布对话流。 此接口暂不支持异步运行。 扣子应用中的对话流 必选 必选 不传 不传 可选 workflow_id 不传 bot_id 如果对话流的输入中包含文件、图片等多模态内容，需要先上传多模态内容以获取文件 ID 或 URL 地址，再将其作为对话流的输入。上传方式包括： 调用 上传文件 API，获取文件 ID，将此 ID 作为对话流的输入。 上传到第三方存储工具中，并获取一个公开可访问的 URL 地址，将此 URL 作为对话流的输入。 调用接口后，你可以从响应的 Done 事件中获得 debug_url，访问链接即可通过可视化界面查看对话流的试运行过程，其中包含每个执行节点的输入输出等详细信息，帮助你在线调试或排障。debug_url 的访问有效期为 7 天，过期后将无法访问。 入参 在扣子应用中执行资源库中的对话流 必选 可选 可选 在智能体中执行资源库中的对话流 必选 app_id

        :param workflow_id: required 待执行的对话流 ID，此对话流应已发布
        :param additional_messages: required 对话中用户问题和历史消息
        :param parameters: required 设置对话流输入参数中的自定义参数 (map[String]any)
        :param app_id: 需要关联的扣子应用 ID
        :param bot_id: 需要关联的智能体 ID
        :param conversation_id: 对话流对应的会话 ID
        :param ext: 用于指定一些额外的字段，例如经纬度、用户ID等
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
        """
        执行对话流

        可选 可选 如果对话流的输入中包含文件、图片等多模态内容，需要先上传多模态内容以获取文件 ID 或 URL 地址，再将其作为对话流的输入。上传方式包括： 调用 上传文件 API，获取文件 ID，将此 ID 作为对话流的输入。 上传到第三方存储工具中，并获取一个公开可访问的 URL 地址，将此 URL 作为对话流的输入。 调用接口后，你可以从响应的 Done 事件中获得 debug_url，访问链接即可通过可视化界面查看对话流的试运行过程，其中包含每个执行节点的输入输出等详细信息，帮助你在线调试或排障。debug_url 的访问有效期为 7 天，过期后将无法访问。 在智能体中执行资源库中的对话流 在扣子应用中执行资源库中的对话流 workflow_id 必选 必选 必选 必选 扣子应用中的对话流 必选 app_id 不传 bot_id 不传 执行已发布的对话流。 接口说明 对话流是基于对话场景的特殊工作流，专门用于处理对话类请求。对话流通过对话的方式和用户交互，并完成复杂的业务逻辑。在应用中添加对话流，将对话中的用户指令拆分为一个个步骤节点，并为其设计用户界面，你可以搭建出适用于移动端或网页端的对话式 AI 应用，实现自动化、智能化的对话流程。关于对话流的详细说明可参考 工作流与对话流 。 此接口为流式响应模式，允许客户端在接收到完整的数据流之前就开始处理数据，例如在对话界面实时展示回复内容，减少客户端等待模型完整回复的时间。 此接口支持包括问答节点、输入节点等可能导致对话中断的节点，对话中断时只需再次调用对话流，在 additional_messages 中指定输入内容，即可继续对话。 此接口可用于调用空间资源库中的对话流，或扣子应用中的对话流。调用这两种对话流时，入参不同： 限制说明 通过 API 方式执行对话流前，应确认此对话流已发布，执行从未发布过的对话流时会返回错误码 4200。如果是扣子应用中的对话流，应先发布扣子应用为 API 服务；如果是空间资源库中的对话流，应先在资源库中发布对话流。 此接口暂不支持异步运行。 入参 必选 不传 conversation_id 可选

        :param workflow_id: required 待执行的对话流 ID，此对话流应已发布
        :param additional_messages: required 对话中用户问题和历史消息
        :param parameters: required 设置对话流输入参数中的自定义参数 (map[String]any)
        :param app_id: 需要关联的扣子应用 ID
        :param bot_id: 需要关联的智能体 ID
        :param conversation_id: 对话流对应的会话 ID
        :param ext: 用于指定一些额外的字段，例如经纬度、用户ID等
        """
        url = f"{self._base_url}/v1/workflows/chat"
        headers: Optional[dict] = kwargs.get("headers")
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
        resp: AsyncIteratorHTTPResponse[str] = await self._requester.arequest(
            "post",
            url,
            True,
            cast=None,
            headers=headers,
            body=body,
        )
        return AsyncStream(
            resp.data, fields=["event", "data"], handler=_chat_stream_handler, raw_response=resp._raw_response
        )
