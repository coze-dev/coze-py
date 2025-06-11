from typing import Optional

from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


class WorkflowNodeExecuteHistory(CozeModel):
    is_finish: bool
    node_output: Optional[str] = None


class WorkflowsRunsRunHistoriesExecuteNodesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def retrieve(self, *, workflow_id: str, execute_id: str, node_execute_uuid: str) -> WorkflowNodeExecuteHistory:
        url = (
            f"{self._base_url}/v1/workflows/{workflow_id}/run_histories/{execute_id}/execute_nodes/{node_execute_uuid}"
        )
        return self._requester.request("get", url, False, cast=WorkflowNodeExecuteHistory)


class AsyncWorkflowsRunsRunHistoriesExecuteNodesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def retrieve(
        self, *, workflow_id: str, execute_id: str, node_execute_uuid: str
    ) -> WorkflowNodeExecuteHistory:
        url = (
            f"{self._base_url}/v1/workflows/{workflow_id}/run_histories/{execute_id}/execute_nodes/{node_execute_uuid}"
        )
        return await self._requester.arequest("get", url, False, cast=WorkflowNodeExecuteHistory)
