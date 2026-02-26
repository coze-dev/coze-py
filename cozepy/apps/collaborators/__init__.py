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
        """
        添加应用协作者

        添加低代码应用的协作者。
        接口限制
        套餐限制：扣子企业版（企业标准版、企业旗舰版）。
        每次请求只能添加一位协作者。如需添加多位，请依次发送请求。
        协作者只能是该工作空间的成员。
        不支持渠道类型 OAuth 应用。使用 OAuth JWT 应用和服务访问令牌时，只需要有对应权限点即可。其余认证方式，只有应用的所有者和协作者能添加协作者。
        主账号内的所有子账号共享同一 API 的流控额度，单个 API 的流控限制为 5 QPS。

        :param app_id: 低代码应用的 ID。 进入应用编排页面，页面 URL 中 `project-ide` 参数后的数字就是应用 ID。例如`https://www.coze.cn/space/7532329396037500982/project-ide/7535386114057***`，应用 ID 为 `7535386114057***`。
        """
        url = f"{self._base_url}/v1/apps/{app_id}/collaborators"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "collaborators": [i.model_dump() for i in collaborators] if collaborators else [],
            }
        )
        return self._requester.request("post", url, False, cast=AddAppCollaboratorResp, headers=headers, body=body)

    def delete(self, *, app_id: str, user_id: str, **kwargs) -> RemoveAppCollaboratorResp:
        """
        删除应用协作者

        删除扣子应用的协作者。
        删除协作者时，扣子会将该协作者创建的工作流、插件等资源转移给应用的所有者。
        接口限制
        主账号内的所有子账号共享同一 API 的流控额度，单个 API 的流控限制为 5 QPS。
        每次请求只能删除一位协作者。如需删除多位，请依次发送请求。
        使用个人访问令牌时，只有应用的所有者和协作者有权删除。使用 OAuth 应用和服务访问令牌时，只需要有对应权限点即可。

        :param app_id: 待删除协作者的扣子应用的 ID。 进入扣子应用编排页面，页面 URL 中 `project-ide` 参数后的数字就是应用 ID。例如`https://www.coze.cn/space/7532329396037500982/project-ide/7535386114057***`，应用 ID 为 `7535386114057***`。
        :param user_id: 待删除协作者的扣子用户 UID。 在扣子平台左下角单击头像，选择**账号设置**，查看账号的 UID。
        """
        url = f"{self._base_url}/v1/apps/{app_id}/collaborators/{user_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("delete", url, False, cast=RemoveAppCollaboratorResp, headers=headers)


class AsyncAppsCollaboratorsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def create(self, *, app_id: str, collaborators: List[AppCollaborator], **kwargs) -> AddAppCollaboratorResp:
        """
        添加应用协作者

        添加低代码应用的协作者。
        接口限制
        套餐限制：扣子企业版（企业标准版、企业旗舰版）。
        每次请求只能添加一位协作者。如需添加多位，请依次发送请求。
        协作者只能是该工作空间的成员。
        不支持渠道类型 OAuth 应用。使用 OAuth JWT 应用和服务访问令牌时，只需要有对应权限点即可。其余认证方式，只有应用的所有者和协作者能添加协作者。
        主账号内的所有子账号共享同一 API 的流控额度，单个 API 的流控限制为 5 QPS。

        :param app_id: 低代码应用的 ID。 进入应用编排页面，页面 URL 中 `project-ide` 参数后的数字就是应用 ID。例如`https://www.coze.cn/space/7532329396037500982/project-ide/7535386114057***`，应用 ID 为 `7535386114057***`。
        """
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
        """
        删除应用协作者

        删除扣子应用的协作者。
        删除协作者时，扣子会将该协作者创建的工作流、插件等资源转移给应用的所有者。
        接口限制
        主账号内的所有子账号共享同一 API 的流控额度，单个 API 的流控限制为 5 QPS。
        每次请求只能删除一位协作者。如需删除多位，请依次发送请求。
        使用个人访问令牌时，只有应用的所有者和协作者有权删除。使用 OAuth 应用和服务访问令牌时，只需要有对应权限点即可。

        :param app_id: 待删除协作者的扣子应用的 ID。 进入扣子应用编排页面，页面 URL 中 `project-ide` 参数后的数字就是应用 ID。例如`https://www.coze.cn/space/7532329396037500982/project-ide/7535386114057***`，应用 ID 为 `7535386114057***`。
        :param user_id: 待删除协作者的扣子用户 UID。 在扣子平台左下角单击头像，选择**账号设置**，查看账号的 UID。
        """
        url = f"{self._base_url}/v1/apps/{app_id}/collaborators/{user_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest("delete", url, False, cast=RemoveAppCollaboratorResp, headers=headers)
