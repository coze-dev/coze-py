from typing import Optional

from cozepy.model import CozeModel, DynamicStrEnum
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


class BotCollaborationMode(DynamicStrEnum):
    SINGLE = "single"
    COLLABORATION = "collaboration"


class UpdateBotCollaborationModeResp(CozeModel):
    pass


class BotsCollaborationModesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def update(
        self, *, bot_id: str, collaboration_mode: BotCollaborationMode, **kwargs
    ) -> UpdateBotCollaborationModeResp:
        """
        开启或关闭智能体多人协作

        开启或关闭智能体多人协作模式。
        开启多人协作后，你才能调用添加智能体的协作者 API 为智能体添加协作者。
        接口限制
        套餐限制：扣子企业版（企业标准版、企业旗舰版）。
        不支持渠道类型 OAuth 应用。使用 OAuth JWT 应用和服务访问令牌时，只需要有对应权限点即可。其余认证方式，只有智能体所有者能开启或关闭智能体的多人协作模式。
        关闭智能体多人协作前，需要先调用删除智能体协作者 API 删除所有协作者。

        :param bot_id: 需要设置协作模式的智能体 ID。 进入智能体的开发页面，开发页面 URL 中 bot 参数后的数字就是智能体 ID。例如`https://www.coze.com/space/341****/bot/73428668*****`，bot ID 为`73428668*****`。
        """
        url = f"{self._base_url}/v1/bots/{bot_id}/collaboration_mode"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "collaboration_mode": collaboration_mode,
        }
        return self._requester.request(
            "post", url, False, cast=UpdateBotCollaborationModeResp, headers=headers, body=body
        )


class AsyncBotsCollaborationModesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def update(
        self, *, bot_id: str, collaboration_mode: BotCollaborationMode, **kwargs
    ) -> UpdateBotCollaborationModeResp:
        """
        开启或关闭智能体多人协作

        开启或关闭智能体多人协作模式。
        开启多人协作后，你才能调用添加智能体的协作者 API 为智能体添加协作者。
        接口限制
        套餐限制：扣子企业版（企业标准版、企业旗舰版）。
        不支持渠道类型 OAuth 应用。使用 OAuth JWT 应用和服务访问令牌时，只需要有对应权限点即可。其余认证方式，只有智能体所有者能开启或关闭智能体的多人协作模式。
        关闭智能体多人协作前，需要先调用删除智能体协作者 API 删除所有协作者。

        :param bot_id: 需要设置协作模式的智能体 ID。 进入智能体的开发页面，开发页面 URL 中 bot 参数后的数字就是智能体 ID。例如`https://www.coze.com/space/341****/bot/73428668*****`，bot ID 为`73428668*****`。
        """
        url = f"{self._base_url}/v1/bots/{bot_id}/collaboration_mode"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "collaboration_mode": collaboration_mode,
        }
        return await self._requester.arequest(
            "post", url, False, cast=UpdateBotCollaborationModeResp, headers=headers, body=body
        )
