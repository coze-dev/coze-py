from enum import Enum, IntEnum
from typing import Optional

from cozepy.model import CozeModel, ListResponse
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


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


class WorkflowsRunsRunHistoriesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def retrieve(self, *, workflow_id: str, execute_id: str) -> WorkflowRunHistory:
        """
        After the workflow runs async, retrieve the execution results.

        docs cn: https://www.coze.cn/docs/developer_guides/workflow_history

        :param workflow_id: The ID of the workflow.
        :param execute_id: The ID of the workflow async execute.
        :return: The result of the workflow execution
        """
        url = f"{self._base_url}/v1/workflows/{workflow_id}/run_histories/{execute_id}"
        res = self._requester.request("get", url, False, ListResponse[WorkflowRunHistory])
        data = res.data[0]
        data._raw_response = res._raw_response
        return data


class AsyncWorkflowsRunsRunHistoriesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def retrieve(self, *, workflow_id: str, execute_id: str) -> WorkflowRunHistory:
        """
        After the workflow runs async, retrieve the execution results.

        docs cn: https://www.coze.cn/docs/developer_guides/workflow_history

        :param workflow_id: The ID of the workflow.
        :param execute_id: The ID of the workflow async execute.
        :return: The result of the workflow execution
        """
        url = f"{self._base_url}/v1/workflows/{workflow_id}/run_histories/{execute_id}"
        res = await self._requester.arequest("get", url, False, ListResponse[WorkflowRunHistory])
        data = res.data[0]
        data._raw_response = res._raw_response
        return data
