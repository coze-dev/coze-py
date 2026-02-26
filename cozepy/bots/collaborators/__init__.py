from typing import List, Optional

from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash


class BotCollaborator(CozeModel):
    user_id: str


class AddBotCollaboratorResp(CozeModel):
    pass


class DeleteBotCollaboratorResp(CozeModel):
    pass


class BotsCollaboratorsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(self, *, bot_id: str, collaborators: List[BotCollaborator], **kwargs) -> AddBotCollaboratorResp:
        """
        添加智能体协作者

        添加智能体的协作者。 接口限制 套餐限制：扣子企业版（企业标准版、企业旗舰版）。 每次请求只能添加一位协作者。如需添加多位，请依次发送请求。 协作者只能是该工作空间的成员。 不支持渠道类型 OAuth 应用。使用 OAuth JWT 应用和服务访问令牌时，只需要有对应权限点即可。其余认证方式，只有 智能体的所有者和协作者 能添加协作者。 主账号内的所有子账号共享同一 API 的流控额度，单个 API 的流控限制为 5 QPS。

        :param bot_id: 需要添加协作者的智能体 ID。 进入智能体编排页面，页面 URL 中 `bot` 参数后的数字就是智能体 ID。例如`https://www.coze.cn/space/341****/bot/73428668*****`，bot ID 为`73428668*****`。
        """
        url = f"{self._base_url}/v1/bots/{bot_id}/collaborators"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "collaborators": [i.model_dump() for i in collaborators] if collaborators else [],
            }
        )
        return self._requester.request("post", url, False, cast=AddBotCollaboratorResp, headers=headers, body=body)

    def delete(self, *, bot_id: str, user_id: str, **kwargs) -> DeleteBotCollaboratorResp:
        """
        删除智能体协作者

        删除智能体的协作者。 接口限制 每次请求只能删除一位协作者。如需删除多位，请依次发送请求。 使用个人访问令牌时，只有智能体的所有者和协作者有权删除。使用 OAuth 应用和服务访问令牌时，只需要有对应权限点即可。 主账号内的所有子账号共享同一 API 的流控额度，单个 API 的流控限制为 5 QPS。

        :param bot_id: 需要删除协作者的智能体 ID。 进入智能体编排页面，页面 URL 中 `bot` 参数后的数字就是智能体 ID。例如`https://www.coze.cn/space/341****/bot/73428668*****`，bot ID 为`73428668*****`。
        :param user_id: 待删除的协作者的扣子用户 UID。 在扣子平台左下角单击头像，选择**账号设置**，查看账号的 UID。
        """
        url = f"{self._base_url}/v1/bots/{bot_id}/collaborators/{user_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("delete", url, False, cast=DeleteBotCollaboratorResp, headers=headers)


class AsyncBotsCollaboratorsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def create(self, *, bot_id: str, collaborators: List[BotCollaborator], **kwargs) -> AddBotCollaboratorResp:
        """
        添加智能体协作者

        添加智能体的协作者。 接口限制 套餐限制：扣子企业版（企业标准版、企业旗舰版）。 每次请求只能添加一位协作者。如需添加多位，请依次发送请求。 协作者只能是该工作空间的成员。 不支持渠道类型 OAuth 应用。使用 OAuth JWT 应用和服务访问令牌时，只需要有对应权限点即可。其余认证方式，只有 智能体的所有者和协作者 能添加协作者。 主账号内的所有子账号共享同一 API 的流控额度，单个 API 的流控限制为 5 QPS。

        :param bot_id: 需要添加协作者的智能体 ID。 进入智能体编排页面，页面 URL 中 `bot` 参数后的数字就是智能体 ID。例如`https://www.coze.cn/space/341****/bot/73428668*****`，bot ID 为`73428668*****`。
        """
        url = f"{self._base_url}/v1/bots/{bot_id}/collaborators"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "collaborators": [i.model_dump() for i in collaborators] if collaborators else [],
            }
        )
        return await self._requester.arequest(
            "post", url, False, cast=AddBotCollaboratorResp, headers=headers, body=body
        )

    async def delete(self, *, bot_id: str, user_id: str, **kwargs) -> DeleteBotCollaboratorResp:
        """
        删除智能体协作者

        删除智能体的协作者。 接口限制 每次请求只能删除一位协作者。如需删除多位，请依次发送请求。 使用个人访问令牌时，只有智能体的所有者和协作者有权删除。使用 OAuth 应用和服务访问令牌时，只需要有对应权限点即可。 主账号内的所有子账号共享同一 API 的流控额度，单个 API 的流控限制为 5 QPS。

        :param bot_id: 需要删除协作者的智能体 ID。 进入智能体编排页面，页面 URL 中 `bot` 参数后的数字就是智能体 ID。例如`https://www.coze.cn/space/341****/bot/73428668*****`，bot ID 为`73428668*****`。
        :param user_id: 待删除的协作者的扣子用户 UID。 在扣子平台左下角单击头像，选择**账号设置**，查看账号的 UID。
        """
        url = f"{self._base_url}/v1/bots/{bot_id}/collaborators/{user_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest("delete", url, False, cast=DeleteBotCollaboratorResp, headers=headers)
