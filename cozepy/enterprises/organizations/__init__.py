from typing import Optional

from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import dump_exclude_none, remove_url_trailing_slash


class CreateEnterpriseOrganizationResp(CozeModel):
    pass


class EnterprisesOrganizationsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(
        self,
        *,
        enterprise_id: str,
        name: str,
        super_admin_user_id: str,
        description: Optional[str] = None,
        **kwargs,
    ) -> CreateEnterpriseOrganizationResp:
        """
        创建组织

        在指定的企业中创建组织。
        接口限制
        套餐限制：扣子企业旗舰版。
        数量限制：一个企业中最多存在 20 个组织。

        :param enterprise_id: 企业 ID，用于标识该组织所属的企业。 你可以在**组织管理** > **组织设置**页面查看企业 ID。 ![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/02db2078f0c84bc2aa189f5cca93d49d~tplv-goo7wpa0wc-image.image =500x)
        """
        url = f"{self._base_url}/v1/enterprises/{enterprise_id}/organizations"
        headers: Optional[dict] = kwargs.get("headers")
        body = dump_exclude_none(
            {
                "name": name,
                "super_admin_user_id": super_admin_user_id,
                "description": description,
            }
        )
        return self._requester.request(
            "post", url, False, cast=CreateEnterpriseOrganizationResp, headers=headers, body=body
        )


class AsyncEnterprisesOrganizationsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def create(
        self,
        *,
        enterprise_id: str,
        name: str,
        super_admin_user_id: str,
        description: Optional[str] = None,
        **kwargs,
    ) -> CreateEnterpriseOrganizationResp:
        """
        创建组织

        在指定的企业中创建组织。
        接口限制
        套餐限制：扣子企业旗舰版。
        数量限制：一个企业中最多存在 20 个组织。

        :param enterprise_id: 企业 ID，用于标识该组织所属的企业。 你可以在**组织管理** > **组织设置**页面查看企业 ID。 ![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/02db2078f0c84bc2aa189f5cca93d49d~tplv-goo7wpa0wc-image.image =500x)
        """
        url = f"{self._base_url}/v1/enterprises/{enterprise_id}/organizations"
        headers: Optional[dict] = kwargs.get("headers")
        body = dump_exclude_none(
            {
                "name": name,
                "super_admin_user_id": super_admin_user_id,
                "description": description,
            }
        )
        return await self._requester.arequest(
            "post", url, False, cast=CreateEnterpriseOrganizationResp, headers=headers, body=body
        )
