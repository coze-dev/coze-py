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
        """删除工作流协作者"""
        url = f"{self._base_url}/v1/workflows/{workflow_id}/collaborators/{user_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("delete", url, False, cast=RemoveWorkflowCollaboratorResp, headers=headers)


class AsyncWorkflowsCollaboratorsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def delete(self, *, user_id: str, workflow_id: str, **kwargs) -> RemoveWorkflowCollaboratorResp:
        """删除工作流协作者"""
        url = f"{self._base_url}/v1/workflows/{workflow_id}/collaborators/{user_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest(
            "delete", url, False, cast=RemoveWorkflowCollaboratorResp, headers=headers
        )
