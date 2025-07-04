import httpx
import pytest

from cozepy import (
    AsyncCoze,
    AsyncTokenAuth,
    Coze,
    EnterpriseMember,
    EnterpriseMemberRole,
    TokenAuth,
)
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_create_enterprise_members(respx_mock, enterprise_id, user_ids):
    respx_mock.post(f"/v1/enterprises/{enterprise_id}/members").mock(
        httpx.Response(
            200,
            json={},
            headers={logid_key(): "logid"},
        )
    )


def mock_delete_enterprise_members(respx_mock, enterprise_id, user_id):
    respx_mock.delete(f"/v1/enterprises/{enterprise_id}/members/{user_id}").mock(
        httpx.Response(
            200,
            json={},
            headers={logid_key(): "logid"},
        )
    )


def mock_update_enterprise_members(respx_mock, enterprise_id, user_id):
    respx_mock.put(f"/v1/enterprises/{enterprise_id}/members/{user_id}").mock(
        httpx.Response(
            200,
            json={},
            headers={logid_key(): "logid"},
        )
    )


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncEnterprisesMembers:
    def test_sync_members_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        enterprise_id = random_hex(10)
        users = [EnterpriseMember(user_id=random_hex(10), role=EnterpriseMemberRole.ENTERPRISE_MEMBER)]
        mock_create_enterprise_members(respx_mock, enterprise_id, [u.user_id for u in users])
        resp = coze.enterprises.members.create(
            enterprise_id=enterprise_id,
            users=users,
        )
        assert resp.response.logid == "logid"

    def test_sync_members_delete(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        enterprise_id = random_hex(10)
        user_id = random_hex(10)
        mock_delete_enterprise_members(respx_mock, enterprise_id, user_id)
        resp = coze.enterprises.members.delete(
            enterprise_id=enterprise_id, user_id=user_id, receiver_user_id=random_hex(10)
        )
        assert resp.response.logid == "logid"

    def test_sync_members_update(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        enterprise_id = random_hex(10)
        user_id = random_hex(10)
        mock_update_enterprise_members(respx_mock, enterprise_id, user_id)
        resp = coze.enterprises.members.update(
            enterprise_id=enterprise_id,
            user_id=user_id,
            role=EnterpriseMemberRole.ENTERPRISE_ADMIN,
        )
        assert resp.response.logid == "logid"


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncEnterprisesMembers:
    async def test_async_members_create(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        enterprise_id = random_hex(10)
        users = [EnterpriseMember(user_id=random_hex(10), role=EnterpriseMemberRole.ENTERPRISE_MEMBER)]
        mock_create_enterprise_members(respx_mock, enterprise_id, [u.user_id for u in users])
        resp = await coze.enterprises.members.create(
            enterprise_id=enterprise_id,
            users=users,
        )
        assert resp.response.logid == "logid"

    async def test_async_members_delete(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        enterprise_id = random_hex(10)
        user_id = random_hex(10)
        mock_delete_enterprise_members(respx_mock, enterprise_id, user_id)
        resp = await coze.enterprises.members.delete(
            enterprise_id=enterprise_id, user_id=user_id, receiver_user_id=random_hex(10)
        )
        assert resp.response.logid == "logid"

    async def test_async_members_update(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        enterprise_id = random_hex(10)
        user_id = random_hex(10)
        mock_update_enterprise_members(respx_mock, enterprise_id, user_id)
        resp = await coze.enterprises.members.update(
            enterprise_id=enterprise_id,
            user_id=user_id,
            role=EnterpriseMemberRole.ENTERPRISE_ADMIN,
        )
        assert resp.response.logid == "logid"
