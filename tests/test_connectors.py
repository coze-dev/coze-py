import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Coze, TokenAuth
from cozepy.connectors.bots import AuditStatus, UpdateConnectorBotResp
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_update_connector_bot(respx_mock, connector_id: str, bot_id: str):
    mock_response = UpdateConnectorBotResp()
    mock_response._raw_response = httpx.Response(
        200,
        json={
            "data": mock_response.model_dump(),
        },
        headers={logid_key(): random_hex(10)},
    )
    route = respx_mock.put(f"/v1/connectors/{connector_id}/bots/{bot_id}")
    route.mock(mock_response._raw_response)


@pytest.mark.respx(base_url="https://api.coze.com")
class TestConnectorsBotsClient:
    """测试ConnectorsBotsClient类"""

    def test_update_approved(self, respx_mock):
        """测试更新Bot审核结果为通过"""
        coze = Coze(auth=TokenAuth(token="token"))
        connector_id = random_hex(10)
        bot_id = random_hex(10)

        mock_update_connector_bot(respx_mock, connector_id, bot_id)

        resp = coze.connectors.bots.update(
            bot_id=bot_id,
            connector_id=connector_id,
            audit_status=AuditStatus.APPROVED,
        )
        assert resp
        assert resp.response.logid


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncConnectorsBotsClient:
    """测试AsyncConnectorsBotsClient类"""

    async def test_update_approved(self, respx_mock):
        """测试异步更新Bot审核结果为通过"""
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        connector_id = random_hex(10)
        bot_id = random_hex(10)

        mock_update_connector_bot(respx_mock, connector_id, bot_id)

        resp = await coze.connectors.bots.update(
            bot_id=bot_id,
            connector_id=connector_id,
            audit_status=AuditStatus.APPROVED,
        )
        assert resp
        assert resp.response.logid
