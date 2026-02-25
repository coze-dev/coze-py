from typing import TYPE_CHECKING, List, Optional

from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash

if TYPE_CHECKING:
    from cozepy.connectors.bots import AsyncConnectorsBotsClient, ConnectorsBotsClient


class UserConfigEnum(CozeModel):
    label: str
    value: str


class UserConfig(CozeModel):
    enums: List[UserConfigEnum]
    key: str


class BindConnectorUserConfigResp(CozeModel):
    pass


class InstallConnectorResp(CozeModel):
    pass


class ConnectorsClient(object):
    """
    渠道客户端

    提供渠道相关功能的客户端类。
    """

    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._bots: Optional[ConnectorsBotsClient] = None

    @property
    def bots(self) -> "ConnectorsBotsClient":
        """
        渠道Bot客户端
        """
        if not self._bots:
            from .bots import ConnectorsBotsClient

            self._bots = ConnectorsBotsClient(base_url=self._base_url, requester=self._requester)
        return self._bots

    def bind(
        self,
        *,
        connector_id: str,
        configs: List[UserConfig],
        user_id: Optional[str] = None,
        **kwargs,
    ) -> BindConnectorUserConfigResp:
        """
        绑定设备

        将设备与自定义渠道绑定。 接口描述 硬件厂商可以调用本 API 将企业内的硬件设备与企业的自定义渠道绑定，当开发者发布智能体到该自定义渠道时，在发布配置页面的设备列表中选择对应的设备，即可快速发布到对应设备。 支持批量绑定多台设备。 创建自定义渠道后，默认未开启 API 绑定设备的能力，如果需要调用本 API，你需要将自定义渠道的渠道 ID 提供给扣子商务经理，申请开通渠道设备绑定的能力，并由商务经理配置设备绑定的 key。

        :param connector_id: 企业自定义渠道的渠道 ID。 自定义渠道 ID 的获取方式如下：在扣子左下角单击头像，在**账号设置** > **发布渠道** > **企业自定义渠道管理**页面查看渠道 ID。自定义渠道入驻扣子的方式可参考[渠道入驻](https://www.coze.cn/open/docs/dev_how_to_guides/channel_integration_overview)文档。
        """
        url = f"{self._base_url}/v1/connectors/{connector_id}/user_configs"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "configs": [i.model_dump() for i in configs] if configs else [],
                "user_id": user_id,
            }
        )
        return self._requester.request("post", url, False, cast=BindConnectorUserConfigResp, headers=headers, body=body)

    def install(self, *, connector_id: str, workspace_id: str, **kwargs) -> InstallConnectorResp:
        """
        添加发布渠道

        为指定空间添加一个发布渠道。 接口说明 在扣子编程中发布智能体或应用时，可发布的渠道范围与工作空间有关。每个工作空间均配置了官方默认发布渠道，例如扣子商店、豆包、API 、SDK 等。除此之外，工作空间中还可以手动添加公共渠道和企业自定义渠道，按需拓展 AI 项目的分发渠道。添加渠道后，空间中的每个开发者都可以将自己的 AI 项目发布到这些渠道中。 添加发布渠道之前，需要获取发布渠道的渠道 ID。 企业自定义渠道：在 我的 > 设置 > 发布渠道 > 我的渠道管理 页面查看当前登录用户已创建的渠道列表，列表中可查看渠道 ID。企业自定义渠道入驻扣子编程的方式可参考 渠道入驻 文档。 公开渠道：联系公开平台的管理员获取渠道 ID。 扣子企业版（企业标准版、企业旗舰版）中，仅 超级管理员和管理员 能添加企业的公共渠道和自定义渠道，成员只能给个人空间添加公共渠道和自定义渠道。

        :param connector_id: 渠道 ID。 * 企业自定义渠道：在**我的**>**设置**>**发布渠道**>**我的渠道管理**页面查看当前登录用户已创建的渠道列表，列表中可查看渠道 ID。企业自定义渠道入驻扣子编程的方式可参考[渠道入驻](https://docs.coze.cn/dev_how_to_guides/channel_integration_overview)文档。 * 公开渠道：联系公开平台的管理员获取渠道 ID。
        """
        url = f"{self._base_url}/v1/connectors/{connector_id}/install"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "workspace_id": workspace_id,
        }
        return self._requester.request("post", url, False, cast=InstallConnectorResp, headers=headers, body=body)


class AsyncConnectorsClient(object):
    """
    异步渠道客户端

    提供异步渠道相关功能的客户端类。
    """

    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._bots: Optional[AsyncConnectorsBotsClient] = None

    @property
    def bots(self) -> "AsyncConnectorsBotsClient":
        """
        异步渠道Bot客户端
        """
        if not self._bots:
            from .bots import AsyncConnectorsBotsClient

            self._bots = AsyncConnectorsBotsClient(base_url=self._base_url, requester=self._requester)
        return self._bots

    async def bind(
        self,
        *,
        connector_id: str,
        configs: List[UserConfig],
        user_id: Optional[str] = None,
        **kwargs,
    ) -> BindConnectorUserConfigResp:
        """
        绑定设备

        将设备与自定义渠道绑定。 接口描述 硬件厂商可以调用本 API 将企业内的硬件设备与企业的自定义渠道绑定，当开发者发布智能体到该自定义渠道时，在发布配置页面的设备列表中选择对应的设备，即可快速发布到对应设备。 支持批量绑定多台设备。 创建自定义渠道后，默认未开启 API 绑定设备的能力，如果需要调用本 API，你需要将自定义渠道的渠道 ID 提供给扣子商务经理，申请开通渠道设备绑定的能力，并由商务经理配置设备绑定的 key。

        :param connector_id: 企业自定义渠道的渠道 ID。 自定义渠道 ID 的获取方式如下：在扣子左下角单击头像，在**账号设置** > **发布渠道** > **企业自定义渠道管理**页面查看渠道 ID。自定义渠道入驻扣子的方式可参考[渠道入驻](https://www.coze.cn/open/docs/dev_how_to_guides/channel_integration_overview)文档。
        """
        url = f"{self._base_url}/v1/connectors/{connector_id}/user_configs"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "configs": [i.model_dump() for i in configs] if configs else [],
                "user_id": user_id,
            }
        )
        return await self._requester.arequest(
            "post", url, False, cast=BindConnectorUserConfigResp, headers=headers, body=body
        )

    async def install(self, *, connector_id: str, workspace_id: str, **kwargs) -> InstallConnectorResp:
        """
        添加发布渠道

        为指定空间添加一个发布渠道。 接口说明 在扣子编程中发布智能体或应用时，可发布的渠道范围与工作空间有关。每个工作空间均配置了官方默认发布渠道，例如扣子商店、豆包、API 、SDK 等。除此之外，工作空间中还可以手动添加公共渠道和企业自定义渠道，按需拓展 AI 项目的分发渠道。添加渠道后，空间中的每个开发者都可以将自己的 AI 项目发布到这些渠道中。 添加发布渠道之前，需要获取发布渠道的渠道 ID。 企业自定义渠道：在 我的 > 设置 > 发布渠道 > 我的渠道管理 页面查看当前登录用户已创建的渠道列表，列表中可查看渠道 ID。企业自定义渠道入驻扣子编程的方式可参考 渠道入驻 文档。 公开渠道：联系公开平台的管理员获取渠道 ID。 扣子企业版（企业标准版、企业旗舰版）中，仅 超级管理员和管理员 能添加企业的公共渠道和自定义渠道，成员只能给个人空间添加公共渠道和自定义渠道。

        :param connector_id: 渠道 ID。 * 企业自定义渠道：在**我的**>**设置**>**发布渠道**>**我的渠道管理**页面查看当前登录用户已创建的渠道列表，列表中可查看渠道 ID。企业自定义渠道入驻扣子编程的方式可参考[渠道入驻](https://docs.coze.cn/dev_how_to_guides/channel_integration_overview)文档。 * 公开渠道：联系公开平台的管理员获取渠道 ID。
        """
        url = f"{self._base_url}/v1/connectors/{connector_id}/install"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "workspace_id": workspace_id,
        }
        return await self._requester.arequest("post", url, False, cast=InstallConnectorResp, headers=headers, body=body)
