from typing import Any, Dict, Optional

from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash


class CreateBenefitLimitationResp(CozeModel):
    pass


class BenefitLimitationsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(
        self,
        *,
        entity_type: str,
        entity_id: Optional[str] = None,
        benefit_info: Dict[str, Any],
        **kwargs,
    ) -> CreateBenefitLimitationResp:
        """
        创建设备权益额度

        创建终端用户的权益额度。 接口描述 你可以调用本 API 创建终端用户的权益额度，用于设置终端用户可使用的资源点或语音时长配额，以便用户在初始阶段免费体验设备功能，同时避免资源的过度使用。 生效对象：权益额度的生效对象可以设置为企业中的所有设备、所有自定义维度的实体、某个设备或某个自定义维度的实体。 额度类型：支持按资源点维度或语音通话时长维度设置配额，你可以为每个设备设置累计可用额度以及时间周期内的额度（例如每日 1000 资源点）。当设备在当前周期内的资源点使用达到周期上限或累计额度上限时，将无法继续使用，直至下一个周期或额度重置。例如设置每个设备累计额度为 5000 资源点，每天可用 1000 资源点。当设备 A 今天的使用资源点达到 1000 上限后，设备 A 今天将无法继续使用，需等到次日才能恢复使用，当设备 A 的累计使用资源点达到 5000 上限后，设备 A 将无法继续使用。 配置的优先级：若同时为单个设备和企业下所有设备配置了额度，则优先使用单个设备的额度。 生效时间：通过扣子编程的 管理设备配额 页面设置的针对企业下所有设备和自定义维度实体的额度，默认有效期为永不过期，即 started_at = 1970-01-01 至 ended_at = 9999-12-31 。若权益生效时间已过期，则该条配额规则会失效。 未配置额度的设备：未设置权益额度的设备，将默认无限制使用资源点。 接口限制 当权益配额的生效范围为企业下所有设备或企业下所有自定义维度的实体时，仅能创建一条累计可用额度和一条时间周期内可用额度。 增购 AI 智能通话许可（系统音色） 的企业，权益额度类型支持配置为 语音通话时长配额（系统音色） ，否则不生效，购买语音通话时长的详细步骤请参见 音视频费用 。 增购 AI 智能通话许可（复刻音色） 的企业，权益额度类型支持配置为 语音通话时长配额（复刻音色） ，否则不生效。 未增购 AI 智能通话许可的企业，权益额度类型仅支持资源点配额。 套餐限制 ：扣子企业旗舰版。 角色限制 ：企业超级管理员和管理员可以调用该 API。 调用此 API 创建设备权益额度之前，需要确保企业下的设备已成功上报了设备信息，否则会导致权益额度对该设备无法生效，设备信息的配置方法可参考 设置设备信息 。
        """
        url = f"{self._base_url}/v1/commerce/benefit/limitations"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "benefit_info": benefit_info,
            }
        )
        return self._requester.request("post", url, False, cast=CreateBenefitLimitationResp, headers=headers, body=body)


class AsyncBenefitLimitationsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def create(
        self,
        *,
        entity_type: str,
        entity_id: Optional[str] = None,
        benefit_info: Dict[str, Any],
        **kwargs,
    ) -> CreateBenefitLimitationResp:
        """
        创建设备权益额度

        创建终端用户的权益额度。 接口描述 你可以调用本 API 创建终端用户的权益额度，用于设置终端用户可使用的资源点或语音时长配额，以便用户在初始阶段免费体验设备功能，同时避免资源的过度使用。 生效对象：权益额度的生效对象可以设置为企业中的所有设备、所有自定义维度的实体、某个设备或某个自定义维度的实体。 额度类型：支持按资源点维度或语音通话时长维度设置配额，你可以为每个设备设置累计可用额度以及时间周期内的额度（例如每日 1000 资源点）。当设备在当前周期内的资源点使用达到周期上限或累计额度上限时，将无法继续使用，直至下一个周期或额度重置。例如设置每个设备累计额度为 5000 资源点，每天可用 1000 资源点。当设备 A 今天的使用资源点达到 1000 上限后，设备 A 今天将无法继续使用，需等到次日才能恢复使用，当设备 A 的累计使用资源点达到 5000 上限后，设备 A 将无法继续使用。 配置的优先级：若同时为单个设备和企业下所有设备配置了额度，则优先使用单个设备的额度。 生效时间：通过扣子编程的 管理设备配额 页面设置的针对企业下所有设备和自定义维度实体的额度，默认有效期为永不过期，即 started_at = 1970-01-01 至 ended_at = 9999-12-31 。若权益生效时间已过期，则该条配额规则会失效。 未配置额度的设备：未设置权益额度的设备，将默认无限制使用资源点。 接口限制 当权益配额的生效范围为企业下所有设备或企业下所有自定义维度的实体时，仅能创建一条累计可用额度和一条时间周期内可用额度。 增购 AI 智能通话许可（系统音色） 的企业，权益额度类型支持配置为 语音通话时长配额（系统音色） ，否则不生效，购买语音通话时长的详细步骤请参见 音视频费用 。 增购 AI 智能通话许可（复刻音色） 的企业，权益额度类型支持配置为 语音通话时长配额（复刻音色） ，否则不生效。 未增购 AI 智能通话许可的企业，权益额度类型仅支持资源点配额。 套餐限制 ：扣子企业旗舰版。 角色限制 ：企业超级管理员和管理员可以调用该 API。 调用此 API 创建设备权益额度之前，需要确保企业下的设备已成功上报了设备信息，否则会导致权益额度对该设备无法生效，设备信息的配置方法可参考 设置设备信息 。
        """
        url = f"{self._base_url}/v1/commerce/benefit/limitations"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "benefit_info": benefit_info,
            }
        )
        return await self._requester.arequest(
            "post", url, False, cast=CreateBenefitLimitationResp, headers=headers, body=body
        )
