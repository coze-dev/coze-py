from enum import Enum
from typing import List, Optional

from cozepy.model import CozeModel, NumberPagedResponse
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash


class WorkspaceRoleType(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class WorkspaceType(str, Enum):
    PERSONAL = "personal"
    TEAM = "team"


class Workspace(CozeModel):
    # workspace id
    id: str
    # workspace name
    name: str
    # workspace icon url
    icon_url: str
    # user in workspace role type
    role_type: WorkspaceRoleType
    # workspace type
    workspace_type: WorkspaceType


class WorkspaceMember(CozeModel):
    user_id: str  # 用户ID
    role_type: WorkspaceRoleType  # 当前用户角色

    user_nickname: Optional[str]  # 昵称（添加成员时不用传）
    user_unique_name: Optional[str]  # 用户名（添加成员时不用传）
    avatar_url: Optional[str]  # 头像 （添加成员时不用传）


class CreateWorkspaceMemberResp(CozeModel):
    pass


class DeleteWorkspaceMemberResp(CozeModel):
    pass


class _PrivateListWorkspacesData(CozeModel, NumberPagedResponse[Workspace]):
    total_count: int
    workspaces: List[Workspace]

    def get_total(self) -> Optional[int]:
        return self.total_count

    def get_has_more(self) -> Optional[bool]:
        return None

    def get_items(self) -> List[Workspace]:
        return self.workspaces


class WorkspacesMembersClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(
        self,
        *,
        workspace_id: str,
        user_list: List[WorkspaceMember],
    ) -> CreateWorkspaceMemberResp:
        url = f"{self._base_url}/v1/workspaces/{workspace_id}/members"
        body = remove_none_values(
            {
                "user_list": [user.model_dump() for user in user_list],
            }
        )
        return self._requester.request("post", url, stream=False, cast=CreateWorkspaceMemberResp, body=body)

    def delete(
        self,
        *,
        workspace_id: str,
        user_id_list: List[str],
    ) -> DeleteWorkspaceMemberResp:
        url = f"{self._base_url}/v1/workspaces/{workspace_id}/members"
        body = remove_none_values(
            {
                "user_id_list": user_id_list,
            }
        )
        return self._requester.request("delete", url, stream=False, cast=DeleteWorkspaceMemberResp, body=body)


class AsyncWorkspacesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def create(
        self,
        *,
        workspace_id: str,
        user_list: List[WorkspaceMember],
    ) -> CreateWorkspaceMemberResp:
        url = f"{self._base_url}/v1/workspaces/{workspace_id}/members"
        body = remove_none_values(
            {
                "user_list": [user.model_dump() for user in user_list],
            }
        )
        return await self._requester.arequest("post", url, stream=False, cast=CreateWorkspaceMemberResp, body=body)

    async def delete(
        self,
        *,
        workspace_id: str,
        user_id_list: List[str],
    ) -> DeleteWorkspaceMemberResp:
        url = f"{self._base_url}/v1/workspaces/{workspace_id}/members"
        body = remove_none_values(
            {
                "user_id_list": user_id_list,
            }
        )
        return await self._requester.arequest("delete", url, stream=False, cast=DeleteWorkspaceMemberResp, body=body)
