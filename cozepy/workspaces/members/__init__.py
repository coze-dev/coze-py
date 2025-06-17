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
    # 团队或企业版成功添加的用户 ID 列表。
    added_success_user_ids: List[str]
    # 个人版中，发起邀请且用户同意加入的用户 ID 列表。
    invited_success_user_ids: List[str]
    # 因用户不存在而导致添加失败的用户 ID 列表。
    not_exist_user_ids: List[str]
    # 用户在该工作空间中已经存在，不重复添加。
    already_joined_user_ids: List[str]
    # 已经发起邀请但用户还未同意加入的用户 ID 列表。
    # 仅个人版的空间添加用户时需要发出邀请，用户同意后才会加入空间。
    already_invited_user_ids: List[str]


class DeleteWorkspaceMemberResp(CozeModel):
    # 成功移除的成员列表。
    removed_success_user_ids: List[str]
    # 不在当前空间中的用户 ID 列表，这些用户不会被处理。
    not_in_workspace_user_ids: List[str]
    # 移除失败，该用户为空间所有者。
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
        """批量邀请用户加入空间

        :param workspace_id: 需要添加用户的空间 ID。
        :param users: 要添加的成员列表，单次最多添加 20 个成员。
        """
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
        """ "批量移除空间中的用户

        :param workspace_id: 需要移除用户的空间 ID。
        :param user_ids: 要移除的成员，单次最多移除 5 个成员。
        """
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
        """查看空间成员列表

        :param workspace_id: 需要查看成员列表的空间 ID。
        :param page_num: 分页查询时的页码。最小值为 1，默认为 1，即从第一页数据开始返回。
        :param page_size: 分页大小。取值范围为 1~50，默认为 20。
        :return: 空间成员列表。
        """
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
        users: List[WorkspaceMember],
        **kwargs,
    ) -> CreateWorkspaceMemberResp:
        """批量邀请用户加入空间

        :param workspace_id: 需要添加用户的空间 ID。
        :param users: 要添加的成员列表，单次最多添加 20 个成员。
        """
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
        """ "批量移除空间中的用户

        :param workspace_id: 需要移除用户的空间 ID。
        :param user_ids: 要移除的成员，单次最多移除 5 个成员。
        """
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
        """查看空间成员列表

        :param workspace_id: 需要查看成员列表的空间 ID。
        :param page_num: 分页查询时的页码。最小值为 1，默认为 1，即从第一页数据开始返回。
        :param page_size: 分页大小。取值范围为 1~50，默认为 20。
        :return: 空间成员列表。
        """
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
