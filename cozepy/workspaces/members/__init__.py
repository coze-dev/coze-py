from typing import List, Optional

from cozepy.model import AsyncNumberPaged, CozeModel, HTTPRequest, NumberPaged
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash
from cozepy.workspaces import WorkspaceRoleType


class WorkspaceMember(CozeModel):
    user_id: str  # 用户ID
    role_type: WorkspaceRoleType  # 当前用户角色

    user_nickname: Optional[str] = None  # 昵称（添加成员时不用传）
    user_unique_name: Optional[str] = None  # 用户名（添加成员时不用传）
    avatar_url: Optional[str] = None  # 头像 （添加成员时不用传）


class CreateWorkspaceMemberResp(CozeModel):
    # 添加成功的用户ID列表
    added_success_user_ids: List[str]
    # 邀请成功的用户ID列表
    invited_success_user_ids: List[str]
    # 不存在用户ID列表
    not_exist_user_ids: List[str]
    # 已加入用户ID列表
    already_joined_user_ids: List[str]
    # 已邀请用户ID列表
    already_invited_user_ids: List[str]


class DeleteWorkspaceMemberResp(CozeModel):
    # 成功移除的成员列表
    removed_success_user_ids: List[str]
    # 不在空间的用户不进行处理
    not_in_workspace_user_ids: List[str]
    # 空间所有者不进行处理
    owner_not_support_remove_user_ids: List[str]


class WorkspacesMembersClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(
        self,
        *,
        workspace_id: str,
        users: List[WorkspaceMember],
        **kwargs,
    ) -> CreateWorkspaceMemberResp:
        url = f"{self._base_url}/v1/workspaces/{workspace_id}/members"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "users": [
                    {
                        "user_id": user.user_id,
                        "role_type": user.role_type,
                    }
                    for user in users
                ],
            }
        )
        return self._requester.request(
            "post", url, stream=False, cast=CreateWorkspaceMemberResp, headers=headers, body=body
        )

    def delete(
        self,
        *,
        workspace_id: str,
        user_ids: List[str],
        **kwargs,
    ) -> DeleteWorkspaceMemberResp:
        url = f"{self._base_url}/v1/workspaces/{workspace_id}/members"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "user_ids": user_ids,
            }
        )
        return self._requester.request(
            "delete", url, stream=False, cast=DeleteWorkspaceMemberResp, headers=headers, body=body
        )

    def list(
        self,
        *,
        workspace_id: str,
        page_num: int = 1,
        page_size: int = 20,
        **kwargs,
    ) -> NumberPaged[WorkspaceMember]:
        url = f"{self._base_url}/v1/workspaces/{workspace_id}/members"
        headers: Optional[dict] = kwargs.get("headers")

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                headers=headers,
                params=remove_none_values(
                    {
                        "page_size": i_page_size,
                        "page_num": i_page_num,
                    }
                ),
                cast=WorkspaceMember,
                stream=False,
            )

        return NumberPaged(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )


class AsyncWorkspacesMembersClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def create(
        self,
        *,
        workspace_id: str,
        user_list: List[WorkspaceMember],
        **kwargs,
    ) -> CreateWorkspaceMemberResp:
        url = f"{self._base_url}/v1/workspaces/{workspace_id}/members"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "user_list": [
                    {
                        "user_id": user.user_id,
                        "role_type": user.role_type,
                    }
                    for user in user_list
                ],
            }
        )
        return await self._requester.arequest(
            "post", url, stream=False, cast=CreateWorkspaceMemberResp, headers=headers, body=body
        )

    async def delete(
        self,
        *,
        workspace_id: str,
        user_ids: List[str],
        **kwargs,
    ) -> DeleteWorkspaceMemberResp:
        url = f"{self._base_url}/v1/workspaces/{workspace_id}/members"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "user_ids": user_ids,
            }
        )
        return await self._requester.arequest(
            "delete", url, stream=False, cast=DeleteWorkspaceMemberResp, headers=headers, body=body
        )

    async def list(
        self,
        *,
        workspace_id: str,
        page_num: int = 1,
        page_size: int = 20,
        **kwargs,
    ) -> AsyncNumberPaged[WorkspaceMember]:
        url = f"{self._base_url}/v1/workspaces/{workspace_id}/members"
        headers: Optional[dict] = kwargs.get("headers")

        async def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "GET",
                url,
                headers=headers,
                params=remove_none_values(
                    {
                        "page_size": i_page_size,
                        "page_num": i_page_num,
                    }
                ),
                cast=WorkspaceMember,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )
