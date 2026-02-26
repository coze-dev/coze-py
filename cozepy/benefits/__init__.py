from typing import List, Optional

from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash


class BenefitBasicInfo(CozeModel):
    user_level: Optional[str] = None


class BenefitItemInfo(CozeModel):
    # 结束时间，单位秒
    end_at: Optional[int] = None
    # 开始时间，单位秒
    start_at: Optional[int] = None
    # 资源使用策略
    strategy: Optional[str] = None
    # 当 Strategy == ByQuota 时, 表示用量上限
    total: Optional[float] = None
    # 当 Strategy == ByQuota 时, 表示已使用量, 若权益无相关用量数据则返回 0
    used: Optional[float] = None


class BenefitStatusInfo(CozeModel):
    """
    基础值
    """

    item_info: Optional[BenefitItemInfo] = None
    status: Optional[str] = None


class BenefitInfo(CozeModel):
    # 基础值
    basic: Optional[BenefitStatusInfo] = None
    benefit_type: Optional[str] = None
    # 实际生效总量
    effective: Optional[BenefitStatusInfo] = None
    # 扩容值，不一定有
    extra: Optional[List[BenefitStatusInfo]] = None
    resource_id: Optional[str] = None


class BenefitOverview(CozeModel):
    basic_info: Optional[BenefitBasicInfo] = None
    benefit_info: Optional[List[BenefitInfo]] = None


class BenefitsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def get(
        self, *, benefit_type_list: Optional[List[str]] = None, resource_id: Optional[str] = None, **kwargs
    ) -> BenefitOverview:
        """
        查询套餐权益

        查询当前账号的套餐权益信息。 接口描述 你可以通过本 API 查询当前账号的以下套餐权益信息： 所属的套餐类型。 扩容管理页面中 API 扩容的信息，包括套餐默认的 API QPS、扩容新增的 API QPS 额度，以及当前实际生效的 API QPS 额度。 套餐权益内通过 MCP 方式调用付费插件的次数限制。

        :param benefit_type_list: 权益类型列表，多个类型用逗号分隔。支持的权益类型如下： * `api_run_qps`： API 扩容的信息，你需要在 `resource_id` 中传入待查询的 API 类型。 * `call_tool_limit`：通过 MCP 方式调用付费插件的次数限制。 默认为空，即返回订阅的套餐类型，不含额外扩容的权益。
        :param resource_id: API 类型，当 `benefit_type_list `为 `api_run_qps`时，需要配置该参数。当前仅支持查询可扩容的 API 类型。枚举值： * `plugin`：插件相关 API 的 QPS 限制。 * `chat`：对话相关的 API 的 QPS 限制。 * `workflow`：工作流相关的 API 的 QPS 限制。
        """
        url = f"{self._base_url}/v1/commerce/benefit/benefits/get"
        params = remove_none_values(
            {
                "benefit_type_list": ",".join(benefit_type_list) if benefit_type_list else None,
                "resource_id": resource_id,
            }
        )
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("get", url, False, cast=BenefitOverview, params=params, headers=headers)


class AsyncBenefitsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def get(
        self, *, benefit_type_list: Optional[List[str]] = None, resource_id: Optional[str] = None, **kwargs
    ) -> BenefitOverview:
        """
        查询套餐权益

        查询当前账号的套餐权益信息。 接口描述 你可以通过本 API 查询当前账号的以下套餐权益信息： 所属的套餐类型。 扩容管理页面中 API 扩容的信息，包括套餐默认的 API QPS、扩容新增的 API QPS 额度，以及当前实际生效的 API QPS 额度。 套餐权益内通过 MCP 方式调用付费插件的次数限制。

        :param benefit_type_list: 权益类型列表，多个类型用逗号分隔。支持的权益类型如下： * `api_run_qps`： API 扩容的信息，你需要在 `resource_id` 中传入待查询的 API 类型。 * `call_tool_limit`：通过 MCP 方式调用付费插件的次数限制。 默认为空，即返回订阅的套餐类型，不含额外扩容的权益。
        :param resource_id: API 类型，当 `benefit_type_list `为 `api_run_qps`时，需要配置该参数。当前仅支持查询可扩容的 API 类型。枚举值： * `plugin`：插件相关 API 的 QPS 限制。 * `chat`：对话相关的 API 的 QPS 限制。 * `workflow`：工作流相关的 API 的 QPS 限制。
        """
        url = f"{self._base_url}/v1/commerce/benefit/benefits/get"
        params = remove_none_values(
            {
                "benefit_type_list": ",".join(benefit_type_list) if benefit_type_list else None,
                "resource_id": resource_id,
            }
        )
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest("get", url, False, cast=BenefitOverview, params=params, headers=headers)
