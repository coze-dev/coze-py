from typing import List, Optional

from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash


class AppCollaborator(CozeModel):
    user_id: str


class AddAppCollaboratorResp(CozeModel):
    pass


class RemoveAppCollaboratorResp(CozeModel):
    pass


class AppsCollaboratorsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(self, *, app_id: str, collaborators: List[AppCollaborator], **kwargs) -> AddAppCollaboratorResp:
        """添加应用协作者"""
        url = f"{self._base_url}/v1/apps/{app_id}/collaborators"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "collaborators": [i.model_dump() for i in collaborators] if collaborators else [],
            }
        )
        return self._requester.request("post", url, False, cast=AddAppCollaboratorResp, headers=headers, body=body)

    def delete(self, *, app_id: str, user_id: str, **kwargs) -> RemoveAppCollaboratorResp:
        """删除应用协作者"""
        url = f"{self._base_url}/v1/apps/{app_id}/collaborators/{user_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("delete", url, False, cast=RemoveAppCollaboratorResp, headers=headers)


class AsyncAppsCollaboratorsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def create(self, *, app_id: str, collaborators: List[AppCollaborator], **kwargs) -> AddAppCollaboratorResp:
        """添加应用协作者"""
        url = f"{self._base_url}/v1/apps/{app_id}/collaborators"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "collaborators": [i.model_dump() for i in collaborators] if collaborators else [],
            }
        )
        return await self._requester.arequest(
            "post", url, False, cast=AddAppCollaboratorResp, headers=headers, body=body
        )

    async def delete(self, *, app_id: str, user_id: str, **kwargs) -> RemoveAppCollaboratorResp:
        """删除应用协作者"""
        url = f"{self._base_url}/v1/apps/{app_id}/collaborators/{user_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest("delete", url, False, cast=RemoveAppCollaboratorResp, headers=headers)
