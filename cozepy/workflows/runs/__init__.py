from enum import Enum
from typing import TYPE_CHECKING, Any, AsyncIterator, Dict, Optional

import httpx

from cozepy.chat import ChatUsage
from cozepy.model import AsyncIteratorHTTPResponse, AsyncStream, CozeModel, IteratorHTTPResponse, Stream
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash

if TYPE_CHECKING:
    from cozepy.workflows.runs.run_histories import (
        AsyncWorkflowsRunsRunHistoriesClient,
        WorkflowsRunsRunHistoriesClient,
    )


class WorkflowRunResult(CozeModel):
    debug_url: str
    # Workflow execution result, usually a JSON serialized string. In some scenarios, a
    # string with a non-JSON structure may be returned.
    data: Optional[str] = ""
    # Execution ID of asynchronous execution. Only returned when the workflow is executed
    # asynchronously (is_async=true). You can use execute_id to call the Query Workflow
    # Asynchronous Execution Result API to obtain the final execution result of the workflow.
    execute_id: Optional[str] = ""
    # 资源使用情况，包含本次 API 调用消耗的 Token 数量等信息。
    # 此处大模型返回的消耗 Token 仅供参考，以火山引擎账单实际为准。
    usage: Optional[ChatUsage] = None


class WorkflowEventType(str, Enum):
    # The output message from the workflow node, such as the output message from
    # the message node or end node. You can view the specific message content in data.
    # 工作流节点输出消息，例如消息节点、结束节点的输出消息。可以在 data 中查看具体的消息内容。
    MESSAGE = "Message"
    # An error has occurred. You can view the error_code and error_message in data to
    # troubleshoot the issue.
    # 报错。可以在 data 中查看 error_code 和 error_message，排查问题。
    ERROR = "Error"
    # End. Indicates the end of the workflow execution, where data is empty.
    # 结束。表示工作流执行结束，此时 data 为空。
    DONE = "Done"
    # Interruption. Indicates the workflow has been interrupted, where the data field
    # contains specific interruption information.
    # 中断。表示工作流中断，此时 data 字段中包含具体的中断信息。
    INTERRUPT = "Interrupt"
    UNKNOWN = "unknown"  # 默认的未知值


class WorkflowEventMessage(CozeModel):
    # The content of the streamed output message.
    # 流式输出的消息内容。
    content: str
    # The name of the node that outputs the message, such as the message node or end node.
    # 输出消息的节点名称，例如消息节点、结束节点。
    node_title: str
    # The message ID of this message within the node, starting at 0, for example, the 5th message of the message node.
    # 此消息在节点中的消息 ID，从 0 开始计数，例如消息节点的第 5 条消息。
    node_seq_id: str
    # Whether the current message is the last data packet for this node.
    # 当前消息是否为此节点的最后一个数据包。
    node_is_finish: bool
    # Additional fields.
    # 额外字段。
    ext: Optional[Dict[str, Any]] = None
    # 资源使用情况，包含本次 API 调用消耗的 Token 数量等信息。
    # 此处大模型返回的消耗 Token 仅供参考，以火山引擎账单实际为准。
    usage: Optional[ChatUsage] = None


class WorkflowEventInterruptData(CozeModel):
    # The workflow interruption event ID, which should be passed back when resuming the workflow.
    # 工作流中断事件 ID，恢复运行时应回传此字段。
    event_id: str
    # The type of workflow interruption, which should be passed back when resuming the workflow.
    # 工作流中断类型，恢复运行时应回传此字段。
    type: int


class WorkflowEventInterrupt(CozeModel):
    # The content of interruption event.
    # 中断控制内容。
    interrupt_data: WorkflowEventInterruptData
    # The name of the node that outputs the message, such as "Question".
    # 输出消息的节点名称，例如“问答”。
    node_title: str


class WorkflowEventError(CozeModel):
    # Status code. 0 represents a successful API call. Other values indicate that the call has failed. You can
    # determine the detailed reason for the error through the error_message field.
    # 调用状态码。0 表示调用成功。其他值表示调用失败。你可以通过 error_message 字段判断详细的错误原因。
    error_code: int
    # Status message. You can get detailed error information when the API call fails.
    # 状态信息。API 调用失败时可通过此字段查看详细错误信息。
    error_message: str


class WorkflowEvent(CozeModel):
    # The event ID of this message in the interface response. It starts from 0.
    id: int
    # The current streaming data packet event.
    event: WorkflowEventType
    message: Optional[WorkflowEventMessage] = None
    interrupt: Optional[WorkflowEventInterrupt] = None
    error: Optional[WorkflowEventError] = None
    unknown: Optional[Dict] = None


def _workflow_stream_handler(data: Dict[str, str], raw_response: httpx.Response) -> Optional[WorkflowEvent]:
    id = int(data["id"])
    event = data["event"]
    event_data = data["data"]  # type: str
    if event == WorkflowEventType.DONE:
        return None
    elif event == WorkflowEventType.MESSAGE:
        return WorkflowEvent(
            id=id,
            event=event,
            message=WorkflowEventMessage.model_validate_json(event_data),
        )
    elif event == WorkflowEventType.ERROR:
        return WorkflowEvent(id=id, event=event, error=WorkflowEventError.model_validate_json(event_data))
    elif event == WorkflowEventType.INTERRUPT:
        return WorkflowEvent(
            id=id,
            event=event,
            interrupt=WorkflowEventInterrupt.model_validate_json(event_data),
        )
    else:
        return WorkflowEvent(id=id, event=WorkflowEventType.UNKNOWN, unknown=data)


class WorkflowsRunsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._run_histories: Optional[WorkflowsRunsRunHistoriesClient] = None

    @property
    def run_histories(self) -> "WorkflowsRunsRunHistoriesClient":
        if not self._run_histories:
            from .run_histories import WorkflowsRunsRunHistoriesClient

            self._run_histories = WorkflowsRunsRunHistoriesClient(base_url=self._base_url, requester=self._requester)
        return self._run_histories

    def stream(
        self,
        *,
        workflow_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        bot_id: Optional[str] = None,
        app_id: Optional[str] = None,
        ext: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Stream[WorkflowEvent]:
        """
        执行工作流（流式响应）
        目前支持流式响应的工作流节点包括 输出节点 、 问答节点 和 开启了流式输出的结束节点 。
        对于不包含这些节点的工作流，可以使用 执行工作流 接口一次性接收响应数据。
        通过 API 方式执行工作流前，应确认此工作流已发布，执行从未发布过的工作流时会返回错误码 4200。
        创建并发布工作流的操作可参考 使用工作流 。
        调用此 API 之前，应先在扣子平台中试运行此工作流。
        如果试运行时需要关联智能体，则调用此 API 执行工作流时，也需要指定 bot_id。
        通常情况下，执行存在数据库节点、变量节点等节点的工作流需要关联智能体。
        执行应用中的工作流时，需要指定 app_id。
        请勿同时指定 bot_id 和 app_id，否则 API 会报错 4000，表示请求参数错误。
        工作流支持的请求大小上限为 20MB，包括输入参数以及运行期间产生的消息历史等所有相关数据。
        此接口为同步接口，如果工作流整体或某些节点运行超时，智能体可能无法提供符合预期的回复，建议将工作流的执行时间控制在 5 分钟以内。
        同步执行时，工作流整体超时时间限制可参考 工作流使用限制 。
        执行已发布的工作流，响应方式为流式响应。
        接口说明 调用 API 执行工作流时，对于支持流式输出的工作流，往往需要使用流式响应方式接收响应数据，例如实时展示工作流的输出信息、呈现打字机效果等。
        在流式响应中，服务端不会一次性发送所有数据，而是以数据流的形式逐条发送数据给客户端，数据流中包含工作流执行过程中触发的各种事件（event），直至处理完毕或处理中断。
        处理结束后，服务端会通过 event: Done 事件提示工作流执行完毕。
        各个事件的说明可参考 返回结果 。
        限制说明 此接口为同步接口，如果工作流整体或某些节点运行超时，Bot 可能无法提供符合预期的回复。
        同步执行时，工作流整体超时时间限制可参考 工作流使用限制 。
        :param workflow_id: required, 待执行的 Workflow ID，此工作流应已发布
        :param parameters: 工作流开始节点的输入参数及取值 (JSON 序列化字符串)
        :param bot_id: 需要关联的智能体 ID
        :param app_id: 该工作流关联的应用的 ID
        :param ext: 用于指定一些额外的字段，非必要可不填写
        """
        url = f"{self._base_url}/v1/workflow/stream_run"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "workflow_id": workflow_id,
                "parameters": parameters,
                "bot_id": bot_id,
                "app_id": app_id,
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
            fields=["id", "event", "data"],
            handler=_workflow_stream_handler,
        )

    def create(
        self,
        *,
        workflow_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        bot_id: Optional[str] = None,
        app_id: Optional[str] = None,
        is_async: bool = False,
        ext: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> WorkflowRunResult:
        """
        执行工作流
        调用此 API 之前，应先在扣子平台中试运行此工作流，如果试运行时需要关联智能体，则调用此 API 执行工作流时，也需要指定智能体ID。
        通常情况下，执行存在数据库节点、变量节点等节点的工作流需要关联智能体。
        未开启工作流异步运行时，工作流整体超时时间为 10 分钟，建议执行时间控制在 5 分钟以内，否则不保障执行结果的准确性。
        详细说明可参考 工作流使用限制 。
        开启工作流异步运行后，工作流整体超时时间为 24 小时。
        执行已发布的工作流。
        接口说明 此接口为非流式响应模式，如果需要采用流式输出，请参考 执行工作流（流式响应） 。
        调用此接口后，你可以从响应中获得 debug_url，访问链接即可通过可视化界面查看工作流的试运行过程，其中包含每个执行节点的输入输出等详细信息，帮助你在线调试或排障。
        扣子个人付费版、企业版（企业标准版、企业旗舰版）用户调用此接口时，支持通过 is_async 参数异步运行工作流，适用于工作流执行耗时较长，导致运行超时的情况。
        异步运行后可通过本接口返回的 execute_id 调用 查询工作流异步执行结果 API 获取工作流的执行结果。
        限制说明 调用此非流式响应 API 时，若 API 在 90 秒内未收到响应，将因超时而断开连接。
        对于执行耗时较长的工作流，建议使用 执行工作流（流式响应） API。
        限制项 节点限制 说明 必须为已发布。
        执行未发布的工作流会返回错误码 4200。
        创建并发布工作流的操作可参考 使用工作流 。
        工作流中不能包含输出节点、开启了流式输出的结束节点。
        请求大小上限 20 MB，包括输入参数及运行期间产生的消息历史等所有相关数据。
        超时时间 工作流发布状态 关联智能体
        :param workflow_id: required, 待执行的 Workflow ID，此工作流应已发布
        :param parameters: 工作流开始节点的输入参数及取值 (JSON 序列化字符串)
        :param bot_id: 需要关联的智能体 ID
        :param app_id: 该工作流关联的应用的 ID
        :param is_async: 是否异步运行 (默认 false)
        :param ext: 用于指定一些额外的字段，非必要可不填写
        """
        url = f"{self._base_url}/v1/workflow/run"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "workflow_id": workflow_id,
                "parameters": parameters,
                "bot_id": bot_id,
                "app_id": app_id,
                "is_async": is_async,
                "ext": ext,
            }
        )
        return self._requester.request("post", url, False, cast=WorkflowRunResult, headers=headers, body=body)

    def resume(
        self,
        *,
        workflow_id: str,
        event_id: str,
        resume_data: str,
        interrupt_type: int,
        **kwargs,
    ) -> Stream[WorkflowEvent]:
        """
        恢复运行工作流（流式响应）

        流式恢复运行已中断的工作流。
        接口说明
        执行包含问答节点的工作流时，智能体会以指定问题向用户提问，并等待用户回答。此时工作流为中断状态，开发者需要调用此接口回答问题，并恢复运行工作流。如果用户的响应和智能体预期提取的信息不匹配，例如缺少必选的字段，或字段数据类型不一致，工作流会再次中断并追问。如果询问 3 次仍未收到符合预期的回复，则判定为工作流执行失败。
        恢复运行工作流（流式响应）和恢复运行工作流 的区别如下：
        如果调用执行工作流（流式响应）API，中断恢复时需要使用恢复运行工作流（流式响应） API，该 API 通过流式返回执行结果。
        如果调用执行工作流 API，中断恢复时需要使用恢复运行工作流  API，该 API 支持同步运行或异步运行返回执行结果。
        限制说明
        最多调用此接口恢复运行 3 次，如果第三次恢复运行时智能体仍未收到符合预期的回复，则判定为工作流执行失败。
        恢复运行后，index 和节点 index 都会重置。
        恢复运行工作流也会产生 token 消耗，且与执行工作流（流式响应）时消耗的 token 数量相同。

        :param workflow_id: 待执行的 Workflow ID，此工作流应已发布
        :param event_id: 工作流执行中断事件 ID
        :param resume_data: 恢复执行时，用户对智能体指定问题的回复
        :param interrupt_type: 中断类型
        """
        url = f"{self._base_url}/v1/workflow/stream_resume"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "workflow_id": workflow_id,
            "event_id": event_id,
            "resume_data": resume_data,
            "interrupt_type": interrupt_type,
        }
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
            fields=["id", "event", "data"],
            handler=_workflow_stream_handler,
        )


class AsyncWorkflowsRunsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._run_histories: Optional[AsyncWorkflowsRunsRunHistoriesClient] = None

    @property
    def run_histories(self) -> "AsyncWorkflowsRunsRunHistoriesClient":
        if not self._run_histories:
            from .run_histories import AsyncWorkflowsRunsRunHistoriesClient

            self._run_histories = AsyncWorkflowsRunsRunHistoriesClient(
                base_url=self._base_url, requester=self._requester
            )
        return self._run_histories

    async def stream(
        self,
        *,
        workflow_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        bot_id: Optional[str] = None,
        app_id: Optional[str] = None,
        ext: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> AsyncIterator[WorkflowEvent]:
        """
        执行工作流（流式响应）
        执行已发布的工作流，响应方式为流式响应。
        接口说明 调用 API 执行工作流时，对于支持流式输出的工作流，往往需要使用流式响应方式接收响应数据，例如实时展示工作流的输出信息、呈现打字机效果等。
        在流式响应中，服务端不会一次性发送所有数据，而是以数据流的形式逐条发送数据给客户端，数据流中包含工作流执行过程中触发的各种事件（event），直至处理完毕或处理中断。
        处理结束后，服务端会通过 event: Done 事件提示工作流执行完毕。
        各个事件的说明可参考 返回结果 。
        限制说明 此接口为同步接口，如果工作流整体或某些节点运行超时，Bot 可能无法提供符合预期的回复。
        同步执行时，工作流整体超时时间限制可参考 工作流使用限制 。
        目前支持流式响应的工作流节点包括 输出节点 、 问答节点 和 开启了流式输出的结束节点 。
        对于不包含这些节点的工作流，可以使用 执行工作流 接口一次性接收响应数据。
        通过 API 方式执行工作流前，应确认此工作流已发布，执行从未发布过的工作流时会返回错误码 4200。
        创建并发布工作流的操作可参考 使用工作流 。
        调用此 API 之前，应先在扣子平台中试运行此工作流。
        如果试运行时需要关联智能体，则调用此 API 执行工作流时，也需要指定 bot_id。
        通常情况下，执行存在数据库节点、变量节点等节点的工作流需要关联智能体。
        执行应用中的工作流时，需要指定 app_id。
        请勿同时指定 bot_id 和 app_id，否则 API 会报错 4000，表示请求参数错误。
        工作流支持的请求大小上限为 20MB，包括输入参数以及运行期间产生的消息历史等所有相关数据。
        此接口为同步接口，如果工作流整体或某些节点运行超时，智能体可能无法提供符合预期的回复，建议将工作流的执行时间控制在 5 分钟以内。
        同步执行时，工作流整体超时时间限制可参考 工作流使用限制 。
        :param workflow_id: required, 待执行的 Workflow ID，此工作流应已发布
        :param parameters: 工作流开始节点的输入参数及取值 (JSON 序列化字符串)
        :param bot_id: 需要关联的智能体 ID
        :param app_id: 该工作流关联的应用的 ID
        :param ext: 用于指定一些额外的字段，非必要可不填写
        """
        url = f"{self._base_url}/v1/workflow/stream_run"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "workflow_id": workflow_id,
                "parameters": parameters,
                "bot_id": bot_id,
                "app_id": app_id,
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
        async for item in AsyncStream(
            resp.data,
            fields=["id", "event", "data"],
            handler=_workflow_stream_handler,
            raw_response=resp._raw_response,
        ):
            yield item

    async def create(
        self,
        *,
        workflow_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        bot_id: Optional[str] = None,
        app_id: Optional[str] = None,
        is_async: bool = False,
        ext: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> WorkflowRunResult:
        """
        执行工作流
        调用此 API 之前，应先在扣子平台中试运行此工作流，如果试运行时需要关联智能体，则调用此 API 执行工作流时，也需要指定智能体ID。
        通常情况下，执行存在数据库节点、变量节点等节点的工作流需要关联智能体。
        超时时间 调用此非流式响应 API 时，若 API 在 90 秒内未收到响应，将因超时而断开连接。
        对于执行耗时较长的工作流，建议使用 执行工作流（流式响应） API。
        说明 关联智能体 请求大小上限 20 MB，包括输入参数及运行期间产生的消息历史等所有相关数据。
        未开启工作流异步运行时，工作流整体超时时间为 10 分钟，建议执行时间控制在 5 分钟以内，否则不保障执行结果的准确性。
        详细说明可参考 工作流使用限制 。
        开启工作流异步运行后，工作流整体超时时间为 24 小时。
        限制项 必须为已发布。
        执行未发布的工作流会返回错误码 4200。
        创建并发布工作流的操作可参考 使用工作流 。
        节点限制 执行已发布的工作流。
        接口说明 此接口为非流式响应模式，如果需要采用流式输出，请参考 执行工作流（流式响应） 。
        调用此接口后，你可以从响应中获得 debug_url，访问链接即可通过可视化界面查看工作流的试运行过程，其中包含每个执行节点的输入输出等详细信息，帮助你在线调试或排障。
        扣子个人付费版、企业版（企业标准版、企业旗舰版）用户调用此接口时，支持通过 is_async 参数异步运行工作流，适用于工作流执行耗时较长，导致运行超时的情况。
        异步运行后可通过本接口返回的 execute_id 调用 查询工作流异步执行结果 API 获取工作流的执行结果。
        限制说明 工作流发布状态 工作流中不能包含输出节点、开启了流式输出的结束节点。
        :param workflow_id: required, 待执行的 Workflow ID，此工作流应已发布
        :param parameters: 工作流开始节点的输入参数及取值 (JSON 序列化字符串)
        :param bot_id: 需要关联的智能体 ID
        :param app_id: 该工作流关联的应用的 ID
        :param is_async: 是否异步运行 (默认 false)
        :param ext: 用于指定一些额外的字段，非必要可不填写
        """
        url = f"{self._base_url}/v1/workflow/run"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "workflow_id": workflow_id,
                "parameters": parameters,
                "bot_id": bot_id,
                "app_id": app_id,
                "is_async": is_async,
                "ext": ext,
            }
        )
        return await self._requester.arequest("post", url, False, cast=WorkflowRunResult, headers=headers, body=body)

    async def resume(
        self,
        *,
        workflow_id: str,
        event_id: str,
        resume_data: str,
        interrupt_type: int,
        **kwargs,
    ) -> AsyncIterator[WorkflowEvent]:
        """
        恢复运行工作流（流式响应）

        流式恢复运行已中断的工作流。
        接口说明
        执行包含问答节点的工作流时，智能体会以指定问题向用户提问，并等待用户回答。此时工作流为中断状态，开发者需要调用此接口回答问题，并恢复运行工作流。如果用户的响应和智能体预期提取的信息不匹配，例如缺少必选的字段，或字段数据类型不一致，工作流会再次中断并追问。如果询问 3 次仍未收到符合预期的回复，则判定为工作流执行失败。
        恢复运行工作流（流式响应）和恢复运行工作流 的区别如下：
        如果调用执行工作流（流式响应）API，中断恢复时需要使用恢复运行工作流（流式响应） API，该 API 通过流式返回执行结果。
        如果调用执行工作流 API，中断恢复时需要使用恢复运行工作流  API，该 API 支持同步运行或异步运行返回执行结果。
        限制说明
        最多调用此接口恢复运行 3 次，如果第三次恢复运行时智能体仍未收到符合预期的回复，则判定为工作流执行失败。
        恢复运行后，index 和节点 index 都会重置。
        恢复运行工作流也会产生 token 消耗，且与执行工作流（流式响应）时消耗的 token 数量相同。

        :param workflow_id: 待执行的 Workflow ID，此工作流应已发布
        :param event_id: 工作流执行中断事件 ID
        :param resume_data: 恢复执行时，用户对智能体指定问题的回复
        :param interrupt_type: 中断类型
        """
        url = f"{self._base_url}/v1/workflow/stream_resume"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "workflow_id": workflow_id,
            "event_id": event_id,
            "resume_data": resume_data,
            "interrupt_type": interrupt_type,
        }
        resp: AsyncIteratorHTTPResponse[str] = await self._requester.arequest(
            "post",
            url,
            True,
            cast=None,
            headers=headers,
            body=body,
        )
        async for item in AsyncStream(
            resp.data,
            fields=["id", "event", "data"],
            handler=_workflow_stream_handler,
            raw_response=resp._raw_response,
        ):
            yield item
