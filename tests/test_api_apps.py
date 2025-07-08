import httpx
import pytest

from cozepy import AppType, AsyncCoze, AsyncTokenAuth, Coze, TokenAuth
from cozepy.api_apps import APIApp
from cozepy.api_apps.events import APIAppEvent
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_create_api_app(respx_mock):
    logid = random_hex(10)
    app_id = random_hex(10)
    respx_mock.post("https://api.coze.com/v1/api_apps").mock(
        httpx.Response(
            200,
            json={
                "data": APIApp(
                    id=app_id,
                    name="app_name",
                    app_type=AppType.NORMAL,
                    verify_token=random_hex(10),
                ).model_dump()
            },
            headers={logid_key(): logid},
        )
    )
    return logid, app_id


def mock_update_api_app(respx_mock):
    logid = random_hex(10)
    respx_mock.put("https://api.coze.com/v1/api_apps/app_id").mock(
        httpx.Response(
            200,
            json={
                "msg": "success",
                "code": 0,
            },
            headers={logid_key(): logid},
        )
    )
    return logid


def mock_delete_api_app(respx_mock):
    logid = random_hex(10)
    respx_mock.delete("https://api.coze.com/v1/api_apps/app_id").mock(
        httpx.Response(
            200,
            json={
                "msg": "success",
                "code": 0,
            },
            headers={logid_key(): logid},
        )
    )
    return logid


def mock_list_api_app(respx_mock, total_count, page):
    logid = random_hex(10)
    respx_mock.get(
        "https://api.coze.com/v1/api_apps",
        params={
            "page_token": str(page),
        },
    ).mock(
        httpx.Response(
            200,
            json={
                "items": [
                    APIApp(
                        id=f"id_{page}",
                        name="app_name",
                        app_type=AppType.NORMAL,
                        verify_token=random_hex(10),
                    ).model_dump()
                ],
                "next_page_token": str(page + 1),
                "has_more": page < total_count,
            },
            headers={logid_key(): logid},
        )
    )
    return logid


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncApiApps:
    def test_sync_api_apps_create_update_delete(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        mock_logid, mock_app_id = mock_create_api_app(respx_mock)
        app = coze.api_apps.create(app_type=AppType.NORMAL, name="app_name")
        assert app
        assert app.response.logid == mock_logid
        assert app.id == mock_app_id

        mock_logid = mock_update_api_app(respx_mock)
        update_resp = coze.api_apps.update(app_id="app_id", name="new_name")
        assert update_resp
        assert update_resp.response.logid == mock_logid

        mock_logid = mock_delete_api_app(respx_mock)
        res = coze.api_apps.delete(app_id="app_id")
        assert res
        assert res.response.logid == mock_logid

    def test_sync_api_apps_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        total = 3
        size = 1
        # 只 mock total 页
        for idx in range(total):
            mock_list_api_app(respx_mock, total_count=total, page=idx + 1)
        resp = coze.api_apps.list(page_token="1", page_size=1)
        assert resp
        ids = []
        for app in resp:
            ids.append(app.id)
        assert ids == [f"id_{i+1}" for i in range(total)]
        total_result = 0
        for page in resp.iter_pages():
            total_result += 1
            assert page
            assert len(page.items) == size
            app = page.items[0]
            assert app.id == f"id_{total_result}"
        assert total_result == total

    def test_sync_api_apps_events(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        api_app_id = "app_id"
        respx_mock.post(f"https://api.coze.com/v1/api_apps/{api_app_id}/events").mock(
            httpx.Response(200, json={"msg": "success", "code": 0})
        )
        respx_mock.delete(f"https://api.coze.com/v1/api_apps/{api_app_id}/events").mock(
            httpx.Response(200, json={"msg": "success", "code": 0})
        )
        respx_mock.get(
            f"https://api.coze.com/v1/api_apps/{api_app_id}/events",
            params={"page_size": 20, "page_token": ""},
        ).mock(
            httpx.Response(
                200,
                json={
                    "items": [
                        APIAppEvent(
                            api_app_id=api_app_id,
                            name="name",
                            description="description",
                            event_type="event_type",
                        ).model_dump()
                    ],
                    "next_page_token": "",
                    "has_more": False,
                },
            )
        )

        coze.api_apps.events.create(api_app_id=api_app_id, event_types=["event_type"])
        coze.api_apps.events.delete(api_app_id=api_app_id, event_types=["event_type"])
        events = coze.api_apps.events.list(api_app_id=api_app_id)
        assert len(events.items) == 1
        assert events.items[0].api_app_id == api_app_id


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncApiApps:
    async def test_async_api_apps_create_update_delete(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        mock_logid, mock_app_id = mock_create_api_app(respx_mock)
        app = await coze.api_apps.create(app_type=AppType.NORMAL, name="app_name")
        assert app
        assert app.response.logid == mock_logid
        assert app.id == mock_app_id

        mock_logid = mock_update_api_app(respx_mock)
        update_resp = await coze.api_apps.update(app_id="app_id", name="new_name")
        assert update_resp
        assert update_resp.response.logid == mock_logid

        mock_logid = mock_delete_api_app(respx_mock)
        res = await coze.api_apps.delete(app_id="app_id")
        assert res
        assert res.response.logid == mock_logid

    async def test_async_api_apps_list(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        total = 3
        size = 1
        # 只 mock total 页
        for idx in range(total):
            mock_list_api_app(respx_mock, total_count=total, page=idx + 1)
        resp = await coze.api_apps.list(page_token="1", page_size=1)
        assert resp
        ids = []
        async for app in resp:
            ids.append(app.id)
        assert ids == [f"id_{i+1}" for i in range(total)]
        total_result = 0
        async for page in resp.iter_pages():
            total_result += 1
            assert page
            assert len(page.items) == size
            app = page.items[0]
            assert app.id == f"id_{total_result}"
        assert total_result == total

    async def test_async_api_apps_events(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        api_app_id = "app_id"
        respx_mock.post(f"https://api.coze.com/v1/api_apps/{api_app_id}/events").mock(
            httpx.Response(200, json={"msg": "success", "code": 0})
        )
        respx_mock.delete(f"https://api.coze.com/v1/api_apps/{api_app_id}/events").mock(
            httpx.Response(200, json={"msg": "success", "code": 0})
        )
        respx_mock.get(
            f"https://api.coze.com/v1/api_apps/{api_app_id}/events",
            params={"page_size": 20, "page_token": ""},
        ).mock(
            httpx.Response(
                200,
                json={
                    "items": [
                        APIAppEvent(
                            api_app_id=api_app_id,
                            name="name",
                            description="description",
                            event_type="event_type",
                        ).model_dump()
                    ],
                    "next_page_token": "",
                    "has_more": False,
                },
            )
        )

        await coze.api_apps.events.create(api_app_id=api_app_id, event_types=["event_type"])
        await coze.api_apps.events.delete(api_app_id=api_app_id, event_types=["event_type"])
        events = await coze.api_apps.events.list(api_app_id=api_app_id)
        assert len(events.items) == 1
        assert events.items[0].api_app_id == api_app_id
