from enum import Enum
from typing import Dict, Any, Iterator

from cozepy.auth import Auth
from cozepy.model import CozeModel
from cozepy.request import Requester


class WorkflowRunResult(CozeModel):
    debug_url: str
    data: str


class Event(str, Enum):
    # The output message from the workflow node, such as the output message from
    # the message node or end node. You can view the specific message content in data.
    # 工作流节点输出消息，例如消息节点、结束节点的输出消息。可以在 data 中查看具体的消息内容。
    message = "Message"

    # An error has occurred. You can view the error_code and error_message in data to
    # troubleshoot the issue.
    # 报错。可以在 data 中查看 error_code 和 error_message，排查问题。
    error = "Error"

    # End. Indicates the end of the workflow execution, where data is empty.
    # 结束。表示工作流执行结束，此时 data 为空。
    done = "Done"

    # Interruption. Indicates the workflow has been interrupted, where the data field
    # contains specific interruption information.
    # 中断。表示工作流中断，此时 data 字段中包含具体的中断信息。
    interrupt = "Interrupt"


class EventMessage(CozeModel):
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
    ext: Dict[str, Any] = None


class EventInterruptData(CozeModel):
    # The workflow interruption event ID, which should be passed back when resuming the workflow.
    # 工作流中断事件 ID，恢复运行时应回传此字段。
    event_id: str

    # The type of workflow interruption, which should be passed back when resuming the workflow.
    # 工作流中断类型，恢复运行时应回传此字段。
    type: int


class EventInterrupt(CozeModel):
    # The content of interruption event.
    # 中断控制内容。
    interrupt_data: EventInterruptData

    # The name of the node that outputs the message, such as "Question".
    # 输出消息的节点名称，例如“问答”。
    node_title: str


class EventError(CozeModel):
    # Status code. 0 represents a successful API call. Other values indicate that the call has failed. You can determine the detailed reason for the error through the error_message field.
    # 调用状态码。0 表示调用成功。其他值表示调用失败。你可以通过 error_message 字段判断详细的错误原因。
    error_code: int

    # Status message. You can get detailed error information when the API call fails.
    # 状态信息。API 调用失败时可通过此字段查看详细错误信息。
    error_message: str


class WorkflowEvent(CozeModel):
    # The event ID of this message in the interface response. It starts from 0.
    id: int

    # The current streaming data packet event.
    event: Event

    message: EventMessage = None

    interrupt: EventInterrupt = None

    error: EventError = None


class WorkflowEventIterator(object):
    def __init__(self, iters: Iterator[bytes]):
        self._iters = iters

    def __iter__(self):
        return self

    def __next__(self) -> WorkflowEvent:
        id = ""
        event = ""
        data = ""
        line = ""
        times = 0

        while times < 3:
            line = next(self._iters).decode("utf-8")
            if line == "":
                continue
            elif line.startswith("id:"):
                if event == "":
                    id = line[3:]
                else:
                    raise Exception(f"invalid event: {line}")
            elif line.startswith("event:"):
                if event == "":
                    event = line[6:].strip()
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
        elif event == Event.message:
            return WorkflowEvent(id=id, event=event, message=EventMessage.model_validate_json(data))
        elif event == Event.error:
            return WorkflowEvent(id=id, event=event, error=EventError.model_validate_json(data))
        elif event == Event.interrupt:
            return WorkflowEvent(id=id, event=event, interrupt=EventInterrupt.model_validate_json(data))
        else:
            raise Exception(f"unknown event: {line}")


class WorkflowsClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester
        self._v1 = None

    def create(
        self, *, workflow_id: str, parameters: Dict[str, Any] = None, bot_id: str = None, ext: Dict[str, Any] = None
    ) -> WorkflowRunResult:
        """
        Run the published workflow.
        This API is in non-streaming response mode. For nodes that support streaming output,
        you should run the API Run workflow (streaming response) to obtain streaming responses.


        执行已发布的工作流。
        此接口为非流式响应模式，对于支持流式输出的节点，应使用接口执行工作流（流式响应）获取流式响应。

        docs en: https://www.coze.com/docs/developer_guides/workflow_run
        docs cn: https://www.coze.cn/docs/developer_guides/workflow_run

        :param workflow_id: The ID of the workflow, which should have been published.
        待执行的 Workflow ID，此工作流应已发布。
        :param parameters: Input parameters and their values for the starting node of the workflow. You can view the
        list of parameters on the arrangement page of the specified workflow.
        工作流开始节点的输入参数及取值，你可以在指定工作流的编排页面查看参数列表。
        :param bot_id: The associated Bot ID required for some workflow executions,
        such as workflows with database nodes, variable nodes, etc.
        需要关联的 Bot ID。 部分工作流执行时需要指定关联的 Bot，例如存在数据库节点、变量节点等节点的工作流。
        :param ext: Used to specify some additional fields in the format of Map[String][String].
        用于指定一些额外的字段，以 Map[String][String] 格式传入。
        :return: The result of the workflow execution
        工作流执行结果
        """
        url = f"{self._base_url}/v1/workflow/run"
        body = {"workflow_id": workflow_id, "parameters": parameters, "bot_id": bot_id, "ext": ext}
        return self._requester.request("post", url, WorkflowRunResult, body=body)

    def stream(
        self,
        *,
        workflow_id: str,
        parameters: Dict[str, Any] = None,
        bot_id: str = None,
        ext: Dict[str, Any] = None,
    ) -> WorkflowEventIterator:
        """
        Execute the published workflow with a streaming response method.
        执行已发布的工作流，响应方式为流式响应。

        docs en: https://www.coze.com/docs/developer_guides/workflow_stream_run
        docs zh: https://www.coze.cn/docs/developer_guides/workflow_stream_run

        :param workflow_id: The ID of the workflow, which should have been published.
        待执行的 Workflow ID，此工作流应已发布。
        :param parameters: Input parameters and their values for the starting node of the workflow. You can view the
        list of parameters on the arrangement page of the specified workflow.
        工作流开始节点的输入参数及取值，你可以在指定工作流的编排页面查看参数列表。
        :param bot_id: The associated Bot ID required for some workflow executions,
        such as workflows with database nodes, variable nodes, etc.
        需要关联的 Bot ID。 部分工作流执行时需要指定关联的 Bot，例如存在数据库节点、变量节点等节点的工作流。
        :param ext: Used to specify some additional fields in the format of Map[String][String].
        用于指定一些额外的字段，以 Map[String][String] 格式传入。
        :return: The result of the workflow execution
        工作流执行结果


        """
        url = f"{self._base_url}/v1/workflow/stream_run"
        body = {"workflow_id": workflow_id, "parameters": parameters, "bot_id": bot_id, "ext": ext}
        return WorkflowEventIterator(self._requester.request("post", url, None, body=body, stream=True))

    def resume(
        self,
        *,
        workflow_id: str,
        event_id: str,
        resume_data: str,
        interrupt_type: int,
    ) -> WorkflowEventIterator:
        """
        恢复运行已中断的工作流。

        docs zh: https://www.coze.cn/docs/developer_guides/workflow_resume

        :param workflow_id: The ID of the workflow, which should have been published.
        待执行的 Workflow ID，此工作流应已发布。
        :param event_id: 工作流执行中断事件 ID。
        :param resume_data:恢复执行时，用户对 Bot 指定问题的回复。回复中应包含问答节点中的必选参数，否则工作流会再次中断并提问。
        :param interrupt_type: 中断类型，你可以从执行工作流（流式响应）的响应信息中获得中断时间的中断类型。
        :return: The result of the workflow execution
        工作流执行结果
        """
        url = f"{self._base_url}/v1/workflow/stream_resume"
        body = {
            "workflow_id": workflow_id,
            "event_id": event_id,
            "resume_data": resume_data,
            "interrupt_type": interrupt_type,
        }
        return WorkflowEventIterator(self._requester.request("post", url, None, body=body, stream=True))
