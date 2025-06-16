from enum import Enum, IntEnum
from typing import TYPE_CHECKING, Dict, Optional

from pydantic import field_validator

from cozepy.model import CozeModel, ListResponse
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash

if TYPE_CHECKING:
    from .execute_nodes import (
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
    # The ID of execute.
    execute_id: str

    # Execute status:
    #   success: Execution succeeded.
    #   running: Execution in progress.
    #   fail: Execution failed.
    execute_status: WorkflowExecuteStatus

    # The Bot ID specified when executing the workflow. Returns 0 if no Bot ID was specified.
    bot_id: str

    # The release connector ID of the agent. By default, only the Agent as API connector is
    # displayed, and the connector ID is 1024.
    connector_id: str

    # User ID, the user_id specified by the ext field when executing the workflow. If not
    # specified, the token applicant's button ID is returned.
    connector_uid: str

    # How the workflow runs:
    #   0: Synchronous operation.
    #   1: Streaming operation.
    #   2: Asynchronous operation.
    run_mode: WorkflowRunMode

    # The Log ID of the asynchronously running workflow. If the workflow is executed abnormally,
    # you can contact the service team to troubleshoot the problem through the Log ID.
    logid: str

    # The start time of the workflow, in Unix time timestamp format, in seconds.
    create_time: int

    # The workflow resume running time, in Unix time timestamp format, in seconds.
    update_time: int

    # The output of the workflow is usually a JSON serialized string, but it may also be a
    # non-JSON structured string.
    output: str

    # Status code. 0 represents a successful API call. Other values indicate that the call has failed. You can
    # determine the detailed reason for the error through the error_message field.
    error_code: int

    # Status message. You can get detailed error information when the API call fails.
    error_message: Optional[str] = ""

    # Workflow trial run debugging page. Visit this page to view the running results, input
    # and output information of each workflow node.
    debug_url: str

    node_execute_status: Optional[Dict[str, WorkflowRunHistoryNodeExecuteStatus]] = None

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
        if self._execute_nodes is None:
            from .execute_nodes import WorkflowsRunsRunHistoriesExecuteNodesClient

            self._execute_nodes = WorkflowsRunsRunHistoriesExecuteNodesClient(
                base_url=self._base_url, requester=self._requester
            )
        return self._execute_nodes

    def retrieve(self, *, workflow_id: str, execute_id: str, **kwargs) -> WorkflowRunHistory:
        """
        After the workflow runs async, retrieve the execution results.

        docs cn: https://www.coze.cn/docs/developer_guides/workflow_history

        :param workflow_id: The ID of the workflow.
        :param execute_id: The ID of the workflow async execute.
        :return: The result of the workflow execution
        """
        url = f"{self._base_url}/v1/workflows/{workflow_id}/run_histories/{execute_id}"
        headers: Optional[dict] = kwargs.get("headers")
        res = self._requester.request("get", url, False, ListResponse[WorkflowRunHistory], headers=headers)
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
        if self._execute_nodes is None:
            from .execute_nodes import AsyncWorkflowsRunsRunHistoriesExecuteNodesClient

            self._execute_nodes = AsyncWorkflowsRunsRunHistoriesExecuteNodesClient(
                base_url=self._base_url, requester=self._requester
            )
        return self._execute_nodes

    async def retrieve(self, *, workflow_id: str, execute_id: str, **kwargs) -> WorkflowRunHistory:
        """
        After the workflow runs async, retrieve the execution results.

        docs cn: https://www.coze.cn/docs/developer_guides/workflow_history

        :param workflow_id: The ID of the workflow.
        :param execute_id: The ID of the workflow async execute.
        :return: The result of the workflow execution
        """
        url = f"{self._base_url}/v1/workflows/{workflow_id}/run_histories/{execute_id}"
        headers: Optional[dict] = kwargs.get("headers")
        res = await self._requester.arequest("get", url, False, ListResponse[WorkflowRunHistory], headers=headers)
        data = res.data[0]
        data._raw_response = res._raw_response
        return data
