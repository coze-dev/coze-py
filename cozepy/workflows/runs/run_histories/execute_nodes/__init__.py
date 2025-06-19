from typing import Optional

from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


class WorkflowNodeExecuteHistory(CozeModel):
    # 节点是否执行完成。true 表示执行已完成，false表示执行未完成。
    is_finish: bool
    # 节点的执行结果输出信息。
    node_output: Optional[str] = None


class WorkflowsRunsRunHistoriesExecuteNodesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def retrieve(
        self, *, workflow_id: str, execute_id: str, node_execute_uuid: str, **kwargs
    ) -> WorkflowNodeExecuteHistory:
        """查询工作流节点的运行结果

        :param workflow_id: 工作流 ID。
        :param execute_id: 工作流执行 ID。
        :param node_execute_uuid: 工作流异步运行结果 API 中返回的节点执行 uuid。
        """
        url = (
            f"{self._base_url}/v1/workflows/{workflow_id}/run_histories/{execute_id}/execute_nodes/{node_execute_uuid}"
        )
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("get", url, False, cast=WorkflowNodeExecuteHistory, headers=headers)


class AsyncWorkflowsRunsRunHistoriesExecuteNodesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def retrieve(
        self, *, workflow_id: str, execute_id: str, node_execute_uuid: str, **kwargs
    ) -> WorkflowNodeExecuteHistory:
        """查询工作流节点的运行结果

        :param workflow_id: 工作流 ID。
        :param execute_id: 工作流执行 ID。
        :param node_execute_uuid: 工作流异步运行结果 API 中返回的节点执行 uuid。
        """
        url = (
            f"{self._base_url}/v1/workflows/{workflow_id}/run_histories/{execute_id}/execute_nodes/{node_execute_uuid}"
        )
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest("get", url, False, cast=WorkflowNodeExecuteHistory, headers=headers)
