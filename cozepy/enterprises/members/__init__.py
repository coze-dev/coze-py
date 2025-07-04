from typing import List, Optional

from cozepy.model import CozeModel, DynamicStrEnum
from cozepy.request import Requester
from cozepy.util import dump_exclude_none, remove_url_trailing_slash


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


class UpdateEnterpriseMemberResp(CozeModel):
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
        url = f"{self._base_url}/v1/enterprises/{enterprise_id}/members"
        headers: Optional[dict] = kwargs.get("headers")
        body = dump_exclude_none(
            {
                "users": users,
            }
        )
        return self._requester.request(
            "post", url, stream=False, cast=CreateEnterpriseMemberResp, headers=headers, body=body
        )

    def delete(
        self,
        *,
        enterprise_id: str,
        user_id: str,
        receiver_user_id: str,
        **kwargs,
    ) -> DeleteEnterpriseMemberResp:
        url = f"{self._base_url}/v1/enterprises/{enterprise_id}/members/{user_id}"
        headers: Optional[dict] = kwargs.get("headers")
        body = dump_exclude_none(
            {
                "receiver_user_id": receiver_user_id,
            }
        )
        return self._requester.request(
            "delete", url, stream=False, cast=DeleteEnterpriseMemberResp, headers=headers, body=body
        )

    def update(
        self,
        *,
        enterprise_id: str,
        user_id: str,
        role: EnterpriseMemberRole,
        **kwargs,
    ) -> UpdateEnterpriseMemberResp:
        url = f"{self._base_url}/v1/enterprises/{enterprise_id}/members/{user_id}"
        headers: Optional[dict] = kwargs.get("headers")
        body = dump_exclude_none(
            {
                "role": role,
            }
        )
        return self._requester.request(
            "put", url, stream=False, cast=UpdateEnterpriseMemberResp, headers=headers, body=body
        )


class AsyncEnterprisesMembersClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def create(
        self,
        *,
        enterprise_id: str,
        users: List[EnterpriseMember],
        **kwargs,
    ) -> CreateEnterpriseMemberResp:
        url = f"{self._base_url}/v1/enterprises/{enterprise_id}/members"
        headers: Optional[dict] = kwargs.get("headers")
        body = dump_exclude_none({"users": users})
        return await self._requester.arequest(
            "post", url, stream=False, cast=CreateEnterpriseMemberResp, headers=headers, body=body
        )

    async def delete(
        self,
        *,
        enterprise_id: str,
        user_id: str,
        receiver_user_id: str,
        **kwargs,
    ) -> DeleteEnterpriseMemberResp:
        url = f"{self._base_url}/v1/enterprises/{enterprise_id}/members/{user_id}"
        headers: Optional[dict] = kwargs.get("headers")
        body = dump_exclude_none(
            {
                "receiver_user_id": receiver_user_id,
            }
        )
        return await self._requester.arequest(
            "delete", url, stream=False, cast=DeleteEnterpriseMemberResp, headers=headers, body=body
        )

    async def update(
        self,
        *,
        enterprise_id: str,
        user_id: str,
        role: EnterpriseMemberRole,
        **kwargs,
    ) -> UpdateEnterpriseMemberResp:
        url = f"{self._base_url}/v1/enterprises/{enterprise_id}/members/{user_id}"
        headers: Optional[dict] = kwargs.get("headers")
        body = dump_exclude_none(
            {
                "role": role,
            }
        )
        return await self._requester.arequest(
            "put", url, stream=False, cast=UpdateEnterpriseMemberResp, headers=headers, body=body
        )
