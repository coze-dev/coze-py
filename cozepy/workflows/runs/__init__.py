from enum import Enum
from typing import Any, AsyncIterator, Dict, Optional

from cozepy.auth import Auth
from cozepy.model import AsyncStream, CozeModel, Stream
from cozepy.request import Requester


class WorkflowRunResult(CozeModel):
    debug_url: str
    data: str


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


def _workflow_stream_handler(data: Dict[str, str], logid: str, is_async: bool = False) -> WorkflowEvent:
    id = int(data["id"])
    event = data["event"]
    event_data = data["data"]  # type: str
    if event == WorkflowEventType.DONE:
        if is_async:
            raise StopAsyncIteration
        raise StopIteration
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
        raise ValueError(f"invalid workflows.event: {event}, {event_data}")


def _sync_workflow_stream_handler(data: Dict[str, str], logid: str) -> WorkflowEvent:
    return _workflow_stream_handler(data, logid=logid, is_async=False)


def _async_workflow_stream_handler(data: Dict[str, str], logid: str) -> WorkflowEvent:
    return _workflow_stream_handler(data, logid=logid, is_async=True)


class WorkflowsRunsClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester

    def create(
        self,
        *,
        workflow_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        bot_id: Optional[str] = None,
        ext: Optional[Dict[str, Any]] = None,
    ) -> WorkflowRunResult:
        """
        Run the published workflow.
        This API is in non-streaming response mode. For nodes that support streaming output,
        you should run the API Run workflow (streaming response) to obtain streaming responses.

        docs en: https://www.coze.com/docs/developer_guides/workflow_run
        docs cn: https://www.coze.cn/docs/developer_guides/workflow_run

        :param workflow_id: The ID of the workflow, which should have been published.
        :param parameters: Input parameters and their values for the starting node of the workflow. You can view the
        list of parameters on the arrangement page of the specified workflow.
        :param bot_id: The associated Bot ID required for some workflow executions,
        such as workflows with database nodes, variable nodes, etc.
        :param ext: Used to specify some additional fields in the format of Map[String][String].
        :return: The result of the workflow execution
        """
        url = f"{self._base_url}/v1/workflow/run"
        body = {
            "workflow_id": workflow_id,
            "parameters": parameters,
            "bot_id": bot_id,
            "ext": ext,
        }
        return self._requester.request("post", url, False, WorkflowRunResult, body=body)

    def stream(
        self,
        *,
        workflow_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        bot_id: Optional[str] = None,
        ext: Optional[Dict[str, Any]] = None,
    ) -> Stream[WorkflowEvent]:
        """
        Execute the published workflow with a streaming response method.

        docs en: https://www.coze.com/docs/developer_guides/workflow_stream_run
        docs zh: https://www.coze.cn/docs/developer_guides/workflow_stream_run

        :param workflow_id: The ID of the workflow, which should have been published.
        :param parameters: Input parameters and their values for the starting node of the workflow. You can view the
        list of parameters on the arrangement page of the specified workflow.
        :param bot_id: The associated Bot ID required for some workflow executions,
        such as workflows with database nodes, variable nodes, etc.
        :param ext: Used to specify some additional fields in the format of Map[String][String].
        :return: The result of the workflow execution
        """
        url = f"{self._base_url}/v1/workflow/stream_run"
        body = {
            "workflow_id": workflow_id,
            "parameters": parameters,
            "bot_id": bot_id,
            "ext": ext,
        }
        steam_iters, logid = self._requester.request(
            "post",
            url,
            True,
            None,
            body=body,
        )
        return Stream(steam_iters, fields=["id", "event", "data"], handler=_sync_workflow_stream_handler, logid=logid)

    def resume(
        self,
        *,
        workflow_id: str,
        event_id: str,
        resume_data: str,
        interrupt_type: int,
    ) -> Stream[WorkflowEvent]:
        """
        docs zh: https://www.coze.cn/docs/developer_guides/workflow_resume

        :param workflow_id: The ID of the workflow, which should have been published.
        :param event_id:
        :param resume_data:
        :param interrupt_type:
        :return: The result of the workflow execution
        """
        url = f"{self._base_url}/v1/workflow/stream_resume"
        body = {
            "workflow_id": workflow_id,
            "event_id": event_id,
            "resume_data": resume_data,
            "interrupt_type": interrupt_type,
        }
        steam_iters, logid = self._requester.request(
            "post",
            url,
            True,
            None,
            body=body,
        )
        return Stream(steam_iters, fields=["id", "event", "data"], handler=_sync_workflow_stream_handler, logid=logid)


class AsyncWorkflowsRunsClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester

    async def create(
        self,
        *,
        workflow_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        bot_id: Optional[str] = None,
        ext: Optional[Dict[str, Any]] = None,
    ) -> WorkflowRunResult:
        """
        Run the published workflow.
        This API is in non-streaming response mode. For nodes that support streaming output,
        you should run the API Run workflow (streaming response) to obtain streaming responses.

        docs en: https://www.coze.com/docs/developer_guides/workflow_run
        docs cn: https://www.coze.cn/docs/developer_guides/workflow_run

        :param workflow_id: The ID of the workflow, which should have been published.
        :param parameters: Input parameters and their values for the starting node of the workflow. You can view the
        list of parameters on the arrangement page of the specified workflow.
        :param bot_id: The associated Bot ID required for some workflow executions,
        such as workflows with database nodes, variable nodes, etc.
        :param ext: Used to specify some additional fields in the format of Map[String][String].
        :return: The result of the workflow execution
        """
        url = f"{self._base_url}/v1/workflow/run"
        body = {
            "workflow_id": workflow_id,
            "parameters": parameters,
            "bot_id": bot_id,
            "ext": ext,
        }
        return await self._requester.arequest("post", url, False, WorkflowRunResult, body=body)

    async def stream(
        self,
        *,
        workflow_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        bot_id: Optional[str] = None,
        ext: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[WorkflowEvent]:
        """
        Execute the published workflow with a streaming response method.

        docs en: https://www.coze.com/docs/developer_guides/workflow_stream_run
        docs zh: https://www.coze.cn/docs/developer_guides/workflow_stream_run

        :param workflow_id: The ID of the workflow, which should have been published.
        :param parameters: Input parameters and their values for the starting node of the workflow. You can view the
        list of parameters on the arrangement page of the specified workflow.
        :param bot_id: The associated Bot ID required for some workflow executions,
        such as workflows with database nodes, variable nodes, etc.
        :param ext: Used to specify some additional fields in the format of Map[String][String].
        :return: The result of the workflow execution
        """
        url = f"{self._base_url}/v1/workflow/stream_run"
        body = {
            "workflow_id": workflow_id,
            "parameters": parameters,
            "bot_id": bot_id,
            "ext": ext,
        }
        steam_iters, logid = await self._requester.arequest(
            "post",
            url,
            True,
            None,
            body=body,
        )
        async for item in AsyncStream(
            steam_iters, fields=["id", "event", "data"], handler=_async_workflow_stream_handler, logid=logid
        ):
            yield item

    async def resume(
        self,
        *,
        workflow_id: str,
        event_id: str,
        resume_data: str,
        interrupt_type: int,
    ) -> AsyncIterator[WorkflowEvent]:
        """
        docs zh: https://www.coze.cn/docs/developer_guides/workflow_resume

        :param workflow_id: The ID of the workflow, which should have been published.
        :param event_id:
        :param resume_data:
        :param interrupt_type:
        :return: The result of the workflow execution
        """
        url = f"{self._base_url}/v1/workflow/stream_resume"
        body = {
            "workflow_id": workflow_id,
            "event_id": event_id,
            "resume_data": resume_data,
            "interrupt_type": interrupt_type,
        }
        steam_iters, logid = await self._requester.arequest(
            "post",
            url,
            True,
            None,
            body=body,
        )
        async for item in AsyncStream(
            steam_iters, fields=["id", "event", "data"], handler=_async_workflow_stream_handler, logid=logid
        ):
            yield item
