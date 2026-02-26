import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Coze, TokenAuth
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_create_enterprise_organization(respx_mock, enterprise_id):
    respx_mock.post(f"/v1/enterprises/{enterprise_id}/organizations").mock(
        httpx.Response(
            200,
            json={},
            headers={logid_key(): "logid"},
        )
    )


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncEnterprisesOrganizations:
    def test_sync_organizations_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        enterprise_id = random_hex(10)
        mock_create_enterprise_organization(respx_mock, enterprise_id)
        resp = coze.enterprises.organizations.create(
            enterprise_id=enterprise_id,
            name="engineering",
            super_admin_user_id=random_hex(10),
            description="sync organization",
        )
        assert resp.response.logid == "logid"


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncEnterprisesOrganizations:
    async def test_async_organizations_create(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        enterprise_id = random_hex(10)
        mock_create_enterprise_organization(respx_mock, enterprise_id)
        resp = await coze.enterprises.organizations.create(
            enterprise_id=enterprise_id,
            name="engineering",
            super_admin_user_id=random_hex(10),
            description="async organization",
        )
        assert resp.response.logid == "logid"
