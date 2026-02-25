import json

import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Coze, TokenAuth
from cozepy.connectors import UserConfig, UserConfigEnum
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


def mock_bind_connector_user_config(respx_mock, connector_id: str):
    logid = random_hex(10)
    route = respx_mock.post(f"/v1/connectors/{connector_id}/user_configs")
    route.mock(
        httpx.Response(
            200,
            json={
                "data": {},
            },
            headers={logid_key(): logid},
        )
    )
    return route, logid


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

    def test_bind(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        connector_id = random_hex(10)
        user_id = random_hex(10)
        configs = [
            UserConfig(
                key="device_id",
                enums=[
                    UserConfigEnum(label="device_1", value="123"),
                ],
            )
        ]
        route, logid = mock_bind_connector_user_config(respx_mock, connector_id)

        resp = coze.connectors.bind(
            connector_id=connector_id,
            configs=configs,
            user_id=user_id,
        )
        assert resp
        assert resp.response.logid == logid

        body = json.loads(route.calls[0].request.content.decode())
        assert body == {
            "configs": [{"key": "device_id", "enums": [{"label": "device_1", "value": "123"}]}],
            "user_id": user_id,
        }

    def test_bind_no_user_id(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        connector_id = random_hex(10)
        configs = [
            UserConfig(
                key="device_id",
                enums=[
                    UserConfigEnum(label="device_1", value="123"),
                ],
            )
        ]
        route, logid = mock_bind_connector_user_config(respx_mock, connector_id)

        resp = coze.connectors.bind(
            connector_id=connector_id,
            configs=configs,
        )
        assert resp
        assert resp.response.logid == logid

        body = json.loads(route.calls[0].request.content.decode())
        assert "user_id" not in body
        assert body["configs"] == [{"key": "device_id", "enums": [{"label": "device_1", "value": "123"}]}]

    def test_bind_empty_configs(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        connector_id = random_hex(10)
        route, logid = mock_bind_connector_user_config(respx_mock, connector_id)

        resp = coze.connectors.bind(
            connector_id=connector_id,
            configs=[],
        )
        assert resp
        assert resp.response.logid == logid

        body = json.loads(route.calls[0].request.content.decode())
        assert body["configs"] == []


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

    async def test_bind(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        connector_id = random_hex(10)
        user_id = random_hex(10)
        configs = [
            UserConfig(
                key="device_id",
                enums=[
                    UserConfigEnum(label="device_1", value="123"),
                ],
            )
        ]
        route, logid = mock_bind_connector_user_config(respx_mock, connector_id)

        resp = await coze.connectors.bind(
            connector_id=connector_id,
            configs=configs,
            user_id=user_id,
        )
        assert resp
        assert resp.response.logid == logid

        body = json.loads(route.calls[0].request.content.decode())
        assert body == {
            "configs": [{"key": "device_id", "enums": [{"label": "device_1", "value": "123"}]}],
            "user_id": user_id,
        }
