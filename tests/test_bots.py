import httpx
import pytest

from cozepy import APIApp, AppType, AsyncCoze, AsyncTokenAuth, Bot, Coze, SimpleBot, TokenAuth
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_simple_bot(bot_id: str):
    return SimpleBot(
        id=bot_id,
        name="bot_name",
        description="description",
        icon_url="icon_url",
        is_published=True,
        updated_at=0,
        owner_user_id=random_hex(10),
        published_at=0,
    )


def mock_create_bot(
    respx_mock,
) -> Bot:
    bot = Bot(
        bot_id="bot_id",
        name="name",
        description="description",
        icon_url="icon_url",
        create_time=0,
        update_time=0,
        version="version",
        logid=random_hex(10),
    )
    bot._raw_response = httpx.Response(
        200,
        json={"data": bot.model_dump()},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.post("/v1/bot/create").mock(bot._raw_response)
    return bot


def mock_update_bot(
    respx_mock,
):
    logid = random_hex(10)
    raw_response = httpx.Response(200, json={"data": None}, headers={logid_key(): logid})
    respx_mock.post("/v1/bot/update").mock(raw_response)
    return logid


def mock_publish_bot(respx_mock) -> Bot:
    bot = Bot(
        bot_id="bot_id",
        name="name",
        description="description",
        icon_url="icon_url",
        create_time=0,
        update_time=0,
        version="version",
        logid=random_hex(10),
    )
    bot._raw_response = httpx.Response(
        200,
        json={"data": bot.model_dump()},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.post("/v1/bot/publish").mock(bot._raw_response)
    return bot


def mock_retrieve_bot(respx_mock) -> Bot:
    bot_id = random_hex(10)
    bot = Bot(
        bot_id=bot_id,
        name="name",
        description="description",
        icon_url="icon_url",
        create_time=0,
        updated_at=0,
        version="version",
        logid=random_hex(10),
        owner_user_id=random_hex(10),
    )
    bot._raw_response = httpx.Response(
        200,
        json={"data": bot.model_dump()},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.get(f"/v1/bots/{bot_id}").mock(bot._raw_response)
    return bot


def mock_list_bot(respx_mock, total_count, page):
    logid = random_hex(10)
    respx_mock.get(
        "https://api.coze.com/v1/bots",
        params={
            "page_index": page,
        },
    ).mock(
        httpx.Response(
            200,
            json={
                "data": {
                    "items": [mock_simple_bot(f"id_{page}").model_dump()],
                    "total": total_count,
                }
            },
            headers={logid_key(): logid},
        )
    )
    return logid


def mock_create_api_app(respx_mock) -> APIApp:
    app = APIApp(
        id="app_id",
        app_type=AppType.NORMAL,
        verify_token="verify_token",
        name="app_name",
        connector_id=None,
        callback_url=None,
    )
    app._raw_response = httpx.Response(
        200,
        json={"data": app.model_dump()},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.post("/v1/api_apps").mock(app._raw_response)
    return app


def mock_update_api_app(respx_mock):
    logid = random_hex(10)
    raw_response = httpx.Response(200, json={"data": None}, headers={logid_key(): logid})
    respx_mock.post("/v1/api_apps/app_id").mock(raw_response)
    return logid


def mock_delete_api_app(respx_mock):
    logid = random_hex(10)
    raw_response = httpx.Response(200, json={"data": None}, headers={logid_key(): logid})
    respx_mock.delete("/v1/api_apps/app_id").mock(raw_response)
    return logid


def mock_list_api_app(respx_mock, total_count, page):
    logid = random_hex(10)
    # 正常页和兜底页都注册
    respx_mock.get(
        "https://api.coze.com/v1/api_apps",
        params={
            "page_size": 1,
            "page_token": str(page),
        },
    ).mock(
        httpx.Response(
            200,
            json={
                "data": {
                    "items": [
                        APIApp(
                            id=f"id_{page}",
                            app_type=AppType.NORMAL,
                            verify_token="verify_token",
                            name="app_name",
                            connector_id=None,
                            callback_url=None,
                        ).model_dump()
                    ]
                    if page <= total_count
                    else [],
                    "next_page_token": str(page + 1) if page < total_count else "",
                }
            },
            headers={logid_key(): logid},
        )
    )
    return logid


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncBots:
    def test_sync_bots_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_bot = mock_create_bot(respx_mock)

        bot = coze.bots.create(space_id="space id", name="name")
        assert bot
        assert bot.response.logid == mock_bot.response.logid
        assert bot.bot_id == mock_bot.bot_id

    def test_sync_bots_update(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_update_bot(respx_mock)

        res = coze.bots.update(bot_id="bot id", name="name")
        assert res
        assert res.response.logid is not None
        assert res.response.logid == mock_logid

    def test_sync_bots_publish(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_bot = mock_publish_bot(respx_mock)

        bot = coze.bots.publish(bot_id="bot id")
        assert bot
        assert bot.response.logid is not None
        assert bot.response.logid == mock_bot.response.logid
        assert bot.bot_id == mock_bot.bot_id

    def test_sync_bots_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_bot = mock_retrieve_bot(respx_mock)

        bot = coze.bots.retrieve(bot_id=mock_bot.bot_id)
        assert bot
        assert bot.response.logid is not None
        assert bot.response.logid == mock_bot.response.logid
        assert bot.bot_id == mock_bot.bot_id

    def test_sync_bots_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        space_id = random_hex(10)
        total = 10
        size = 1
        for idx in range(total):
            mock_list_bot(respx_mock, total_count=total, page=idx + 1)

        # no iter
        resp = coze.bots.list(space_id=space_id, page_num=1, page_size=1)
        assert resp
        assert resp.has_more is True

        # iter dataset
        total_result = 0
        for bot in resp:
            total_result += 1
            assert bot
            assert bot.bot_id == f"id_{total_result}"
        assert total_result == total

        # iter page
        total_result = 0
        for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.has_more == (total_result < total)
            assert len(page.items) == size
            bot = page.items[0]
            assert bot.bot_id == f"id_{total_result}"
        assert total_result == total


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncBots:
    async def test_async_bots_create(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_bot = mock_create_bot(respx_mock)

        bot = await coze.bots.create(space_id="space id", name="name")
        assert bot
        assert bot.response.logid is not None
        assert bot.response.logid == mock_bot.response.logid
        assert bot.bot_id == mock_bot.bot_id

    async def test_async_bots_update(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_logid = mock_update_bot(respx_mock)

        res = await coze.bots.update(bot_id="bot id", name="name")
        assert res
        assert res.response.logid is not None
        assert res.response.logid == mock_logid

    async def test_async_bots_publish(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_bot = mock_publish_bot(respx_mock)

        bot = await coze.bots.publish(bot_id="bot id")
        assert bot
        assert bot.response.logid is not None
        assert bot.response.logid == mock_bot.response.logid
        assert bot.bot_id == mock_bot.bot_id

    async def test_async_bots_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_bot = mock_retrieve_bot(respx_mock)

        bot = await coze.bots.retrieve(bot_id=mock_bot.bot_id)
        assert bot
        assert bot.response.logid is not None
        assert bot.response.logid == mock_bot.response.logid
        assert bot.bot_id == mock_bot.bot_id

    async def test_async_bots_list(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        space_id = random_hex(10)
        total = 10
        size = 1
        for idx in range(total):
            mock_list_bot(respx_mock, total_count=total, page=idx + 1)

        # no iter
        resp = await coze.bots.list(space_id=space_id, page_num=1, page_size=1)
        assert resp
        assert resp.has_more is True

        # iter dataset
        total_result = 0
        async for bot in resp:
            total_result += 1
            assert bot
            assert bot.bot_id == f"id_{total_result}"
        assert total_result == total

        # iter page
        total_result = 0
        async for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.has_more == (total_result < total)
            assert len(page.items) == size
            bot = page.items[0]
            assert bot.bot_id == f"id_{total_result}"
        assert total_result == total


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncAPIApps:
    def test_sync_api_apps_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        mock_app = mock_create_api_app(respx_mock)
        app = coze.api_apps.create(app_type=AppType.NORMAL, name="app_name")
        assert app
        assert app.response.logid == mock_app.response.logid
        assert app.id == mock_app.id

    def test_sync_api_apps_update(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        mock_logid = mock_update_api_app(respx_mock)
        res = coze.api_apps.update(app_id="app_id", name="new_name")
        assert res
        assert res.response.logid == mock_logid

    def test_sync_api_apps_delete(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
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
        # 迭代所有 app
        ids = [app.id for app in resp]
        assert ids == [f"id_{i+1}" for i in range(total)]
        # 迭代所有 page
        total_result = 0
        for page in resp.iter_pages():
            total_result += 1
            assert page
            assert len(page.items) == size
            app = page.items[0]
            assert app.id == f"id_{total_result}"
        assert total_result == total


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncAPIApps:
    async def test_async_api_apps_create(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        mock_app = mock_create_api_app(respx_mock)
        app = await coze.api_apps.create(app_type=AppType.NORMAL, name="app_name")
        assert app
        assert app.response.logid == mock_app.response.logid
        assert app.id == mock_app.id

    async def test_async_api_apps_update(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        mock_logid = mock_update_api_app(respx_mock)
        res = await coze.api_apps.update(app_id="app_id", name="new_name")
        assert res
        assert res.response.logid == mock_logid

    async def test_async_api_apps_delete(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
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
