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

    def create(self, *, enterprise_id: str, users: List[EnterpriseMember], **kwargs) -> CreateEnterpriseMemberResp:
        """
        添加企业成员

        添加员工到企业。 在火山引擎创建用户后， 默认会自动将用户添加至企业 ，若未成功添加，你可以调用本 API 将用户添加至企业。火山引擎创建用户的具体方法请参见 成员管理 。 接口限制 套餐限制 ：扣子企业版（企业标准版、企业旗舰版）。 本 API 仅支持添加员工（火山子用户），不支持添加外部成员（访客）。 添加成员总数不能超过企业标准版权益中的成员数量上限（100 个成员），否则会提示 777074011错误。 每次请求只能添加一位成员。如需添加多位，请依次发送请求。 该 API 不支持并发请求。

        :param enterprise_id: 企业 ID，用于标识用户所属的企业。 你可以在组织管理 > 组织设置页面查看企业 ID。 ![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/02db2078f0c84bc2aa189f5cca93d49d~tplv-goo7wpa0wc-image.image =500x)
        """
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

    def update(
        self,
        *,
        enterprise_id: str,
        user_id: str,
        role: EnterpriseMemberRole,
        **kwargs,
    ) -> UpdateEnterpriseMemberResp:
        """
        修改企业员工的角色

        修改企业员工的角色。 企业员工角色包括企业管理员和企业普通成员，你可以通过本 API 修改企业员工的角色。 接口限制 不能修改访客的角色。

        :param enterprise_id: 企业 ID，待修改的员工所属的企业。 企业 ID 的获取方法如下： 在左侧导航栏中单击**组织管理**，URL 中 `enterprise` 参数后的数字就是enterprise_id。例如，在 URL `https://www.coze.cn/enterprise/volcano_2105850***/`中，`volcano_2105850***`就是 enterprise_id。
        :param user_id: 待修改员工的扣子用户 UID。 你可以调用火山引擎的 [ListCozeUser-成员列表](https://api.volcengine.com/api-docs/view?serviceCode=coze&version=2025-06-01&action=ListCozeUser) API，其中 `CozeUserId`的值即为扣子用户 UID。
        """
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


class AsyncEnterprisesMembersClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def create(
        self, *, enterprise_id: str, users: List[EnterpriseMember], **kwargs
    ) -> CreateEnterpriseMemberResp:
        """
        添加企业成员

        添加员工到企业。 在火山引擎创建用户后， 默认会自动将用户添加至企业 ，若未成功添加，你可以调用本 API 将用户添加至企业。火山引擎创建用户的具体方法请参见 成员管理 。 接口限制 套餐限制 ：扣子企业版（企业标准版、企业旗舰版）。 本 API 仅支持添加员工（火山子用户），不支持添加外部成员（访客）。 添加成员总数不能超过企业标准版权益中的成员数量上限（100 个成员），否则会提示 777074011错误。 每次请求只能添加一位成员。如需添加多位，请依次发送请求。 该 API 不支持并发请求。

        :param enterprise_id: 企业 ID，用于标识用户所属的企业。 你可以在组织管理 > 组织设置页面查看企业 ID。 ![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/02db2078f0c84bc2aa189f5cca93d49d~tplv-goo7wpa0wc-image.image =500x)
        """
        url = f"{self._base_url}/v1/enterprises/{enterprise_id}/members"
        headers: Optional[dict] = kwargs.get("headers")
        body = dump_exclude_none({"users": users})
        return await self._requester.arequest(
            "post", url, stream=False, cast=CreateEnterpriseMemberResp, headers=headers, body=body
        )

    async def update(
        self,
        *,
        enterprise_id: str,
        user_id: str,
        role: EnterpriseMemberRole,
        **kwargs,
    ) -> UpdateEnterpriseMemberResp:
        """
        修改企业员工的角色

        修改企业员工的角色。 企业员工角色包括企业管理员和企业普通成员，你可以通过本 API 修改企业员工的角色。 接口限制 不能修改访客的角色。

        :param enterprise_id: 企业 ID，待修改的员工所属的企业。 企业 ID 的获取方法如下： 在左侧导航栏中单击**组织管理**，URL 中 `enterprise` 参数后的数字就是enterprise_id。例如，在 URL `https://www.coze.cn/enterprise/volcano_2105850***/`中，`volcano_2105850***`就是 enterprise_id。
        :param user_id: 待修改员工的扣子用户 UID。 你可以调用火山引擎的 [ListCozeUser-成员列表](https://api.volcengine.com/api-docs/view?serviceCode=coze&version=2025-06-01&action=ListCozeUser) API，其中 `CozeUserId`的值即为扣子用户 UID。
        """
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
