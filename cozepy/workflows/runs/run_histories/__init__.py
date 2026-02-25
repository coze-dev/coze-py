from enum import Enum, IntEnum
from typing import TYPE_CHECKING, Dict, Optional

from pydantic import field_validator

from cozepy.chat import ChatUsage
from cozepy.model import CozeModel, ListResponse
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash

if TYPE_CHECKING:
    from cozepy.workflows.runs.run_histories.execute_nodes import (
        AsyncWorkflowsRunsRunHistoriesExecuteNodesClient,
        WorkflowsRunsRunHistoriesExecuteNodesClient,
    )


class WorkflowExecuteStatus(str, Enum):
    # Execution succeeded.
    SUCCESS = "Success"
    # Execution in progress.
    RUNNING = "Running"
    # Execution failed.
    FAIL = "Fail"


class WorkflowRunMode(IntEnum):
    SYNCHRONOUS = 0
    STREAMING = 1
    ASYNCHRONOUS = 2


class WorkflowRunHistoryNodeExecuteStatus(CozeModel):
    # 工作流中的节点 ID。
    node_id: str
    # 工作流中的节点是否已经运行结束。
    is_finish: bool
    # 工作流上次运行的时间，采用 Unix 时间戳格式，单位为秒。
    update_time: int
    # 节点每次执行的 ID，用于追踪和识别工作流中特定节点的单次执行情况。
    node_execute_uuid: str
    # 当前节点在循环节点中的循环次数。
    loop_index: Optional[int] = None
    # 当前节点在批处理节点中的执行次数。
    batch_index: Optional[int] = None
    # 子流程执行的 ID。
    sub_execute_id: Optional[str] = None


class WorkflowRunHistory(CozeModel):
    # 执行 ID。
    execute_id: str
    # 执行状态。Success：执行成功。Running：执行中。Fail：执行失败。
    execute_status: WorkflowExecuteStatus
    # 执行工作流时指定的 Bot ID。返回 0 表示未指定智能体 ID。
    bot_id: str
    # 智能体的发布渠道 ID，默认仅显示 Agent as API 渠道，渠道 ID 为 1024。
    connector_id: str
    # 用户 ID，执行工作流时通过 ext 字段指定的 user_id。如果未指定，则返回 Token 申请人的扣子 ID。
    connector_uid: str
    # 工作流的运行方式：0：同步运行。1：流式运行。2：异步运行。
    run_mode: WorkflowRunMode
    # 工作流异步运行的 Log ID。如果工作流执行异常，可以联系服务团队通过 Log ID 排查问题。
    logid: str
    # 工作流运行开始时间，Unixtime 时间戳格式，单位为秒。
    create_time: int
    # 工作流的恢复运行时间，Unixtime 时间戳格式，单位为秒。
    update_time: int
    # 工作流的输出，通常为 JSON 序列化字符串，也有可能是非 JSON 结构的字符串。
    output: str
    # 执行失败调用状态码。0 表示调用成功。其他值表示调用失败。你可以通过 error_message 字段判断详细的错误原因。
    error_code: int
    # 状态信息。为 API 调用失败时可通过此字段查看详细错误信息。
    error_message: Optional[str] = ""
    # 工作流试运行调试页面。访问此页面可查看每个工作流节点的运行结果、输入输出等信息。
    debug_url: str
    node_execute_status: Optional[Dict[str, WorkflowRunHistoryNodeExecuteStatus]] = None
    # 资源使用情况，包含本次 API 调用消耗的 Token 数量等信息。
    # 此处大模型返回的消耗 Token 仅供参考，以火山引擎账单实际为准。
    usage: Optional[ChatUsage] = None
    # 工作流的输出是否因为过大被清理。true：已清理。false：未清理。
    is_output_trimmed: bool

    @field_validator("error_code", mode="before")
    @classmethod
    def error_code_empty_str_to_zero(cls, v):
        if v == "":
            return 0
        return v


class WorkflowsRunsRunHistoriesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._execute_nodes: Optional[WorkflowsRunsRunHistoriesExecuteNodesClient] = None

    @property
    def execute_nodes(self) -> "WorkflowsRunsRunHistoriesExecuteNodesClient":
        if not self._execute_nodes:
            from .execute_nodes import WorkflowsRunsRunHistoriesExecuteNodesClient

            self._execute_nodes = WorkflowsRunsRunHistoriesExecuteNodesClient(
                base_url=self._base_url, requester=self._requester
            )
        return self._execute_nodes

    def retrieve(self, *, execute_id: str, workflow_id: str, **kwargs) -> WorkflowRunHistory:
        """
        查询工作流异步执行结果

        工作流异步运行后，查看执行结果。 接口说明 调用 执行工作流 或 恢复运行工作流 API 时，如果选择异步运行工作流，响应信息中会返回 execute_id，开发者可以通过本 API 查询指定事件的执行结果。 限制说明 本 API 的流控限制请参见 API 介绍 。 工作流的 输出节点 的输出数据最多保存 24 小时， 结束节点 为 7 天。 输出节点的输出内容超过 1MB 时，无法保证返回内容的完整性。

        :param execute_id: 工作流执行 ID。调用接口[执行工作流](https://www.coze.cn/docs/developer_guides/workflow_run)，如果选择异步执行工作流，响应信息中会返回 execute_id。
        :param workflow_id: 待执行的 Workflow ID，此工作流应已发布。 进入 Workflow 编排页面，在页面 URL 中，workflow 参数后的数字就是 Workflow ID。例如 https://www.coze.com/work_flow?space_id=42463***&workflow_id=73505836754923***，Workflow ID 为 73505836754923***。
        """
        url = f"{self._base_url}/v1/workflows/{workflow_id}/run_histories/{execute_id}"
        headers: Optional[dict] = kwargs.get("headers")
        res = self._requester.request("get", url, False, cast=ListResponse[WorkflowRunHistory], headers=headers)
        data = res.data[0]
        data._raw_response = res._raw_response
        return data


class AsyncWorkflowsRunsRunHistoriesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._execute_nodes: Optional[AsyncWorkflowsRunsRunHistoriesExecuteNodesClient] = None

    @property
    def execute_nodes(self) -> "AsyncWorkflowsRunsRunHistoriesExecuteNodesClient":
        if not self._execute_nodes:
            from .execute_nodes import AsyncWorkflowsRunsRunHistoriesExecuteNodesClient

            self._execute_nodes = AsyncWorkflowsRunsRunHistoriesExecuteNodesClient(
                base_url=self._base_url, requester=self._requester
            )
        return self._execute_nodes

    async def retrieve(self, *, execute_id: str, workflow_id: str, **kwargs) -> WorkflowRunHistory:
        """
        查询工作流异步执行结果

        工作流异步运行后，查看执行结果。 接口说明 调用 执行工作流 或 恢复运行工作流 API 时，如果选择异步运行工作流，响应信息中会返回 execute_id，开发者可以通过本 API 查询指定事件的执行结果。 限制说明 本 API 的流控限制请参见 API 介绍 。 工作流的 输出节点 的输出数据最多保存 24 小时， 结束节点 为 7 天。 输出节点的输出内容超过 1MB 时，无法保证返回内容的完整性。

        :param execute_id: 工作流执行 ID。调用接口[执行工作流](https://www.coze.cn/docs/developer_guides/workflow_run)，如果选择异步执行工作流，响应信息中会返回 execute_id。
        :param workflow_id: 待执行的 Workflow ID，此工作流应已发布。 进入 Workflow 编排页面，在页面 URL 中，workflow 参数后的数字就是 Workflow ID。例如 https://www.coze.com/work_flow?space_id=42463***&workflow_id=73505836754923***，Workflow ID 为 73505836754923***。
        """
        url = f"{self._base_url}/v1/workflows/{workflow_id}/run_histories/{execute_id}"
        headers: Optional[dict] = kwargs.get("headers")
        res = await self._requester.arequest("get", url, False, cast=ListResponse[WorkflowRunHistory], headers=headers)
        data = res.data[0]
        data._raw_response = res._raw_response
        return data
