from typing import Optional

from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


class WorkflowNodeExecuteHistory(CozeModel):
    # 节点是否执行完成。true 表示执行已完成，false表示执行未完成。
    is_finish: bool
    # 执行成功
    node_output: Optional[str] = None


class WorkflowsRunsRunHistoriesExecuteNodesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def retrieve(
        self,
        *,
        execute_id: str,
        node_execute_uuid: str,
        workflow_id: str,
        **kwargs,
    ) -> WorkflowNodeExecuteHistory:
        """
        查询输出节点的执行结果

        查询输出节点的执行结果。 接口描述 通过 查询工作流异步执行结果 API 查询工作流执行结果时，如果工作流输出节点的输出内容超过 1MB，查询工作流异步执行结果 API 无法返回完整的输出节点内容。需要调用本 API，根据工作流的执行 ID 以及 查询工作流异步执行结果 API 返回的节点执行 UUID，逐一查询每个节点的输出内容。 接口限制 本 API 的流控限制请参见 API 介绍 。 输出节点的输出数据最多保存 24 小时。 仅支持查询输出节点的执行结果，不支持查询结束节点的执行结果。 输出节点的输出内容超过1MB 时，无法保证返回内容的完整性。

        :param execute_id: 工作流的执行 ID。调用接口[执行工作流](https://www.coze.cn/docs/developer_guides/workflow_run)，如果选择异步执行工作流，响应信息中会返回 execute_id。
        :param node_execute_uuid: [工作流异步执行结果](https://www.coze.cn/open/docs/developer_guides/workflow_history) API 中返回的节点执行 uuid。
        :param workflow_id: 要执行的 Workflow ID，需要先完成发布 Workflow 的操作。 进入 Workflow 编排页，在页面 URL 中，workflow 参数后的数字就是 Workflow ID。例如： https://www.coze.com/work_flow?space_id=73119690542463***&workflow_id=73505836754923*** , Workflow ID 为 73505836754923*** 。
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
        self,
        *,
        execute_id: str,
        node_execute_uuid: str,
        workflow_id: str,
        **kwargs,
    ) -> WorkflowNodeExecuteHistory:
        """
        查询输出节点的执行结果

        查询输出节点的执行结果。 接口描述 通过 查询工作流异步执行结果 API 查询工作流执行结果时，如果工作流输出节点的输出内容超过 1MB，查询工作流异步执行结果 API 无法返回完整的输出节点内容。需要调用本 API，根据工作流的执行 ID 以及 查询工作流异步执行结果 API 返回的节点执行 UUID，逐一查询每个节点的输出内容。 接口限制 本 API 的流控限制请参见 API 介绍 。 输出节点的输出数据最多保存 24 小时。 仅支持查询输出节点的执行结果，不支持查询结束节点的执行结果。 输出节点的输出内容超过1MB 时，无法保证返回内容的完整性。

        :param execute_id: 工作流的执行 ID。调用接口[执行工作流](https://www.coze.cn/docs/developer_guides/workflow_run)，如果选择异步执行工作流，响应信息中会返回 execute_id。
        :param node_execute_uuid: [工作流异步执行结果](https://www.coze.cn/open/docs/developer_guides/workflow_history) API 中返回的节点执行 uuid。
        :param workflow_id: 要执行的 Workflow ID，需要先完成发布 Workflow 的操作。 进入 Workflow 编排页，在页面 URL 中，workflow 参数后的数字就是 Workflow ID。例如： https://www.coze.com/work_flow?space_id=73119690542463***&workflow_id=73505836754923*** , Workflow ID 为 73505836754923*** 。
        """
        url = (
            f"{self._base_url}/v1/workflows/{workflow_id}/run_histories/{execute_id}/execute_nodes/{node_execute_uuid}"
        )
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest("get", url, False, cast=WorkflowNodeExecuteHistory, headers=headers)
