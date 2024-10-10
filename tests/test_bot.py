import httpx
import pytest

from cozepy import AsyncCoze, Bot, Coze, SimpleBot, TokenAuth


def mock_get_bot_list(respx_mock, total, page):
    respx_mock.get(
        "https://api.coze.com/v1/space/published_bots_list",
        params={
            "page_index": page,
        },
    ).mock(
        httpx.Response(
            200,
            json={
                "data": {
                    "space_bots": [
                        SimpleBot(
                            bot_id=f"id_{page}",
                            bot_name="bot_name",
                            description="description",
                            icon_url="icon_url",
                            publish_time="publish_time",
                        ).model_dump()
                    ],
                    "total": total,
                }
            },
        )
    )


@pytest.mark.respx(base_url="https://api.coze.com")
class TestBot:
    def test_sync_bot_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/bot/create").mock(
            httpx.Response(
                200,
                json={
                    "data": Bot(
                        bot_id="bot_id",
                        name="name",
                        description="description",
                        icon_url="icon_url",
                        create_time=0,
                        update_time=0,
                        version="version",
                    ).model_dump()
                },
            )
        )

        bot = coze.bots.create(space_id="space id", name="name")
        assert bot
        assert bot.bot_id == "bot_id"

    def test_sync_bot_update(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/bot/update").mock(httpx.Response(200, json={"data": None}))

        coze.bots.update(bot_id="bot id", name="name")

    def test_sync_bot_publish(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/bot/publish").mock(
            httpx.Response(
                200,
                json={
                    "data": Bot(
                        bot_id="bot_id",
                        name="name",
                        description="description",
                        icon_url="icon_url",
                        create_time=0,
                        update_time=0,
                        version="version",
                    ).model_dump()
                },
            )
        )

        bot = coze.bots.publish(bot_id="bot id")
        assert bot
        assert bot.bot_id == "bot_id"

    def test_sync_bot_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.get("/v1/bot/get_online_info").mock(
            httpx.Response(
                200,
                json={
                    "data": Bot(
                        bot_id="bot_id",
                        name="name",
                        description="description",
                        icon_url="icon_url",
                        create_time=0,
                        update_time=0,
                        version="version",
                    ).model_dump()
                },
            )
        )

        bot = coze.bots.retrieve(bot_id="bot id")
        assert bot
        assert bot.bot_id == "bot_id"

    def test_sync_bot_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_get_bot_list(
            respx_mock,
            total=10,
            page=1,
        )

        resp = coze.bots.list(space_id="space id", page_size=1)
        assert resp
        assert resp.total == 10
        assert len(resp.items) == 1

    def test_sync_bot_iterator(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        total = 10
        for idx in range(total):
            mock_get_bot_list(respx_mock, total=total, page=idx + 1)

        total_result = 0
        for idx, bot in enumerate(coze.bots.list(space_id="space id", page_size=1)):
            total_result += 1
            assert bot
            assert bot.bot_id == f"id_{idx + 1}"
        assert total_result == total

    def test_sync_bot_page_iterator(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        total = 10
        size = 1
        for idx in range(total):
            mock_get_bot_list(
                respx_mock,
                total=total,
                page=idx + 1,
            )

        total_result = 0
        for idx, page in enumerate(coze.bots.list(space_id="space id", page_size=1).iter_pages()):
            total_result += 1
            assert page
            assert page.total == total
            assert len(page.items) == size
            bot = page.items[0]
            assert bot.bot_id == f"id_{idx + 1}"
        assert total_result == total


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncBot:
    async def test_async_bot_create(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/bot/create").mock(
            httpx.Response(
                200,
                json={
                    "data": Bot(
                        bot_id="bot_id",
                        name="name",
                        description="description",
                        icon_url="icon_url",
                        create_time=0,
                        update_time=0,
                        version="version",
                    ).model_dump()
                },
            )
        )

        bot = await coze.bots.create(space_id="space id", name="name")
        assert bot
        assert bot.bot_id == "bot_id"

    async def test_async_bot_update(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/bot/update").mock(httpx.Response(200, json={"data": None}))

        await coze.bots.update(bot_id="bot id", name="name")

    async def test_async_bot_publish(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/bot/publish").mock(
            httpx.Response(
                200,
                json={
                    "data": Bot(
                        bot_id="bot_id",
                        name="name",
                        description="description",
                        icon_url="icon_url",
                        create_time=0,
                        update_time=0,
                        version="version",
                    ).model_dump()
                },
            )
        )

        bot = await coze.bots.publish(bot_id="bot id")
        assert bot
        assert bot.bot_id == "bot_id"

    async def test_async_bot_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.get("/v1/bot/get_online_info").mock(
            httpx.Response(
                200,
                json={
                    "data": Bot(
                        bot_id="bot_id",
                        name="name",
                        description="description",
                        icon_url="icon_url",
                        create_time=0,
                        update_time=0,
                        version="version",
                    ).model_dump()
                },
            )
        )

        bot = await coze.bots.retrieve(bot_id="bot id")
        assert bot
        assert bot.bot_id == "bot_id"

    async def test_async_bot_list(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        total = 10
        mock_get_bot_list(respx_mock, total=total, page=1)

        resp = await coze.bots.list(space_id="space id", page_num=1)
        assert resp
        assert resp.total == total
        assert len(resp.items) == 1

    async def test_async_bot_iterator(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        total = 10
        for idx in range(total):
            mock_get_bot_list(respx_mock, total=total, page=idx + 1)

        resp = await coze.bots.list(space_id="space id", page_num=1, page_size=1)

        total_result = 0
        async for bot in resp:
            total_result += 1
            assert bot
            assert bot.bot_id == f"id_{total_result}"
        assert total_result == total

    async def test_async_bot_page_iterator(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        total = 10
        for idx in range(total):
            mock_get_bot_list(respx_mock, total=total, page=idx + 1)

        resp = await coze.bots.list(space_id="space id", page_num=1, page_size=1)

        total_result = 0
        async for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.total == total
            assert len(page.items) == 1
            bot = page.items[0]
            assert bot.bot_id == f"id_{total_result}"
        assert total_result == total
