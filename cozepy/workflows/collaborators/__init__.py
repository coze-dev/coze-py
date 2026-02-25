from typing import Optional

from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


class RemoveWorkflowCollaboratorResp(CozeModel):
    pass


class WorkflowsCollaboratorsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def delete(self, *, user_id: str, workflow_id: str, **kwargs) -> RemoveWorkflowCollaboratorResp:
        """
        删除工作流协作者

        删除工作流协作者。 接口限制 每次请求只能删除一位协助者。如需删除多位，请依次发送请求。 主账号内的所有子账号共享同一 API 的流控额度，单个 API 的流控限制为 5 QPS。 使用个人访问令牌时，只有工作流的所有者和协作者有权删除。使用 OAuth 应用和服务访问令牌时，只需要有对应权限点即可。

        :param user_id: 待删除的协作者的扣子用户 UID。 在扣子平台左下角单击头像，选择**账号设置**，查看账号的 UID。
        :param workflow_id: 需要删除协作者的工作流 ID。 进入工作流编排页面，在页面 URL 中，`workflow` 参数后的数字就是 Workflow ID。例如 `https://www.coze.com/work_flow?space_id=42463***&workflow_id=73505836754923***`，Workflow ID 为 `73505836754923***`。
        """
        url = f"{self._base_url}/v1/workflows/{workflow_id}/collaborators/{user_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("delete", url, False, cast=RemoveWorkflowCollaboratorResp, headers=headers)


class AsyncWorkflowsCollaboratorsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def delete(self, *, user_id: str, workflow_id: str, **kwargs) -> RemoveWorkflowCollaboratorResp:
        """
        删除工作流协作者

        删除工作流协作者。 接口限制 每次请求只能删除一位协助者。如需删除多位，请依次发送请求。 主账号内的所有子账号共享同一 API 的流控额度，单个 API 的流控限制为 5 QPS。 使用个人访问令牌时，只有工作流的所有者和协作者有权删除。使用 OAuth 应用和服务访问令牌时，只需要有对应权限点即可。

        :param user_id: 待删除的协作者的扣子用户 UID。 在扣子平台左下角单击头像，选择**账号设置**，查看账号的 UID。
        :param workflow_id: 需要删除协作者的工作流 ID。 进入工作流编排页面，在页面 URL 中，`workflow` 参数后的数字就是 Workflow ID。例如 `https://www.coze.com/work_flow?space_id=42463***&workflow_id=73505836754923***`，Workflow ID 为 `73505836754923***`。
        """
        url = f"{self._base_url}/v1/workflows/{workflow_id}/collaborators/{user_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest(
            "delete", url, False, cast=RemoveWorkflowCollaboratorResp, headers=headers
        )
