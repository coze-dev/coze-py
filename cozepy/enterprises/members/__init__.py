from typing import List, Optional

from cozepy.model import AsyncNumberPaged, CozeModel, DynamicStrEnum, HTTPRequest, NumberPaged
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash


class EnterpriseMemberRole(DynamicStrEnum):
    ENTERPRISE_ADMIN = "enterprise_admin"  # 企业管理员
    ENTERPRISE_MEMBER = "enterprise_member"  # 企业成员


class EnterpriseMember(CozeModel):
    user_id: str  # 用户ID
    role: EnterpriseMemberRole  # 当前用户角色


class CreateEnterpriseMemberResp(CozeModel):
    pass


class DeleteEnterpriseMemberResp(CozeModel):
    pass


class EnterprisesMembersClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(
        self,
        *,
        enterprise_id: str,
        users: List[EnterpriseMember],
        **kwargs,
    ) -> CreateEnterpriseMemberResp:
        """批量邀请用户加入企业

        :param enterprise_id: 需要添加用户的企业 ID。
        :param users: 要添加的成员列表。
        """
        url = f"{self._base_url}/v1/enterprises/{enterprise_id}/members"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "users": [
                    {
                        "user_id": user.user_id,
                        "role": user.role,
                    }
                    for user in users
                ],
            }
        )
        return self._requester.request(
            "post", url, stream=False, cast=CreateEnterpriseMemberResp, headers=headers, body=body
        )

    def delete(
        self,
        *,
        enterprise_id: str,
        user_ids: List[str],
        **kwargs,
    ) -> DeleteEnterpriseMemberResp:
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


class AsyncEnterprisesMembersClient(object):
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
