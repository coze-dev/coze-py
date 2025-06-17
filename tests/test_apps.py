import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Coze, SimpleApp, TokenAuth
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_list_apps(respx_mock, total_count, page):
    logid = random_hex(10)
    respx_mock.get(
        "https://api.coze.com/v1/apps",
        params={
            "page_index": page,
        },
    ).mock(
        httpx.Response(
            200,
            json={
                "data": {
                    "items": [
                        SimpleApp(
                            id=f"id_{page}",
                            name="app_name",
                            description="description",
                            icon_url="icon_url",
                            is_published=True,
                            owner_user_id="owner_id",
                            updated_at=1234567890,
                        ).model_dump()
                    ],
                    "total": total_count,
                }
            },
            headers={logid_key(): logid},
        )
    )
    return logid


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncApps:
    def test_sync_apps_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        workspace_id = random_hex(10)
        total = 5
        size = 1
        for idx in range(total):
            mock_list_apps(respx_mock, total_count=total, page=idx + 1)

        resp = coze.apps.list(workspace_id=workspace_id, page_num=1, page_size=1)
        assert resp
        assert resp.has_more is True

        total_result = 0
        for app in resp:
            total_result += 1
            assert app
            assert app.id == f"id_{total_result}"
        assert total_result == total

        total_result = 0
        for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.has_more == (total_result < total)
            assert len(page.items) == size
            app = page.items[0]
            assert app.id == f"id_{total_result}"
        assert total_result == total


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncApps:
    async def test_async_apps_list(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        workspace_id = random_hex(10)
        total = 5
        size = 1
        for idx in range(total):
            mock_list_apps(respx_mock, total_count=total, page=idx + 1)

        resp = await coze.apps.list(workspace_id=workspace_id, page_num=1, page_size=1)
        assert resp
        assert resp.has_more is True

        total_result = 0
        async for app in resp:
            total_result += 1
            assert app
            assert app.id == f"id_{total_result}"
        assert total_result == total

        total_result = 0
        async for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.has_more == (total_result < total)
            assert len(page.items) == size
            app = page.items[0]
            assert app.id == f"id_{total_result}"
        assert total_result == total
