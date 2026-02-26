import json

import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Coze, TokenAuth
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_create_benefit_limitation(respx_mock):
    logid = random_hex(10)
    route = respx_mock.post("/v1/commerce/benefit/limitations")
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


def build_benefit_info():
    return {
        "benefit_type": "resource_point",
        "limit": 1000,
        "active_mode": "absolute_time",
    }


@pytest.mark.respx(base_url="https://api.coze.com")
class TestBenefitLimitations:
    def test_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        route, logid = mock_create_benefit_limitation(respx_mock)
        entity_id = random_hex(10)
        benefit_info = build_benefit_info()

        resp = coze.benefit_limitations.create(
            entity_type="single_device",
            entity_id=entity_id,
            benefit_info=benefit_info,
        )
        assert resp
        assert resp.response.logid == logid

        body = json.loads(route.calls[0].request.content.decode())
        assert body == {
            "entity_type": "single_device",
            "entity_id": entity_id,
            "benefit_info": benefit_info,
        }

    def test_create_without_entity_id(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        route, logid = mock_create_benefit_limitation(respx_mock)
        benefit_info = build_benefit_info()

        resp = coze.benefit_limitations.create(
            entity_type="enterprise_all_devices",
            benefit_info=benefit_info,
        )
        assert resp
        assert resp.response.logid == logid

        body = json.loads(route.calls[0].request.content.decode())
        assert body == {
            "entity_type": "enterprise_all_devices",
            "benefit_info": benefit_info,
        }


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncBenefitLimitations:
    async def test_create(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        route, logid = mock_create_benefit_limitation(respx_mock)
        entity_id = random_hex(10)
        benefit_info = build_benefit_info()

        resp = await coze.benefit_limitations.create(
            entity_type="single_device",
            entity_id=entity_id,
            benefit_info=benefit_info,
        )
        assert resp
        assert resp.response.logid == logid

        body = json.loads(route.calls[0].request.content.decode())
        assert body == {
            "entity_type": "single_device",
            "entity_id": entity_id,
            "benefit_info": benefit_info,
        }
