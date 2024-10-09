import httpx
import pytest

from cozepy import AsyncCoze, Bot, Coze, SimpleBot, TokenAuth


@pytest.mark.respx(base_url="https://api.coze.com")
class TestBot:
    def test_bot_create(self, respx_mock):
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

    def test_bot_update(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/bot/update").mock(httpx.Response(200, json={"data": None}))

        coze.bots.update(bot_id="bot id", name="name")

    def test_bot_publish(self, respx_mock):
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

    def test_retrieve(self, respx_mock):
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

    def test_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.get("/v1/space/published_bots_list").mock(
            httpx.Response(
                200,
                json={
                    "data": {
                        "space_bots": [
                            SimpleBot(
                                bot_id="bot_id",
                                bot_name="bot_name",
                                description="description",
                                icon_url="icon_url",
                                publish_time="publish_time",
                            ).model_dump()
                        ],
                        "total": 1,
                    }
                },
            )
        )

        resp = coze.bots.list(space_id="space id")
        assert resp
        assert resp.total == 1
        assert len(resp.items) == 1


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncBot:
    async def test_bot_create(self, respx_mock):
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

    async def test_bot_update(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/bot/update").mock(httpx.Response(200, json={"data": None}))

        await coze.bots.update(bot_id="bot id", name="name")

    async def test_publish(self, respx_mock):
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

    async def test_retrieve(self, respx_mock):
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

    async def test_list(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.get("/v1/space/published_bots_list").mock(
            httpx.Response(
                200,
                json={
                    "data": {
                        "space_bots": [
                            SimpleBot(
                                bot_id="bot_id",
                                bot_name="bot_name",
                                description="description",
                                icon_url="icon_url",
                                publish_time="publish_time",
                            ).model_dump()
                        ],
                        "total": 1,
                    }
                },
            )
        )

        resp = await coze.bots.list(space_id="space id")
        assert resp
        assert resp.total == 1
        assert len(resp.items) == 1
