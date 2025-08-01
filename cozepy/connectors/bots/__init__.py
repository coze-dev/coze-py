from enum import Enum
from typing import Optional

from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


class AuditStatus(int, Enum):
    """
    审核状态枚举

    用于表示Bot渠道审核的不同状态。
    """

    PENDING = 1  # 审核中
    APPROVED = 2  # 审核通过
    REJECTED = 3  # 审核不通过


class UpdateConnectorBotResp(CozeModel):
    pass


class ConnectorsBotsClient(object):
    """
    渠道Bot客户端

    提供渠道Bot相关功能的客户端类，包括更新Bot渠道审核结果等功能。
    """

    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def update(
        self,
        *,
        bot_id: str,
        connector_id: str,
        audit_status: Optional[AuditStatus] = None,
        reason: Optional[str] = None,
        **kwargs,
    ) -> UpdateConnectorBotResp:
        """
        更新Bot渠道审核结果

        通过此接口可以更新指定Bot在特定渠道的审核结果，包括通过或拒绝审核。

        docs: https://www.coze.cn/open/docs/developer_guides/update_review_result

        :param bot_id: Bot ID
        :param connector_id: 渠道ID
        :param audit_status: 审核结果状态，可选值：AuditStatus.PENDING（1-审核中）、AuditStatus.APPROVED（2-审核通过）、AuditStatus.REJECTED（3-审核不通过）
        :param reason: 审核意见，当audit_status为3（审核不通过）时必填
        :return: 返回更新审核结果后的响应信息
        """
        url = f"{self._base_url}/v1/connectors/{connector_id}/bots/{bot_id}"
        headers: Optional[dict] = kwargs.get("headers")

        body = {
            "audit_status": audit_status,
            "reason": reason,
        }
        return self._requester.request("put", url, False, UpdateConnectorBotResp, headers=headers, body=body)


class AsyncConnectorsBotsClient(object):
    """
    异步渠道Bot客户端

    提供异步渠道Bot相关功能的客户端类，包括更新Bot渠道审核结果等功能。
    """

    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def update(
        self,
        *,
        bot_id: str,
        connector_id: str,
        audit_status: Optional[AuditStatus] = None,
        reason: Optional[str] = None,
        **kwargs,
    ) -> UpdateConnectorBotResp:
        """
        异步更新Bot渠道审核结果

        通过此接口可以异步更新指定Bot在特定渠道的审核结果，包括通过或拒绝审核。

        :param bot_id: Bot ID
        :param connector_id: 渠道ID
        :param audit_status: 审核结果状态，可选值：AuditStatus.PENDING（1-审核中）、AuditStatus.APPROVED（2-审核通过）、AuditStatus.REJECTED（3-审核不通过）
        :param reason: 审核意见，当audit_status为3（审核不通过）时必填
        :return: 返回更新审核结果后的响应信息
        """
        url = f"{self._base_url}/v1/connectors/{connector_id}/bots/{bot_id}"
        headers: Optional[dict] = kwargs.get("headers")

        body = {
            "audit_status": audit_status,
            "reason": reason,
        }
        return await self._requester.arequest("put", url, False, UpdateConnectorBotResp, headers=headers, body=body)
