import httpx
import pytest

from cozepy import (
    APIApp,
    AppType,
    AsyncCoze,
    AsyncTokenAuth,
    Bot,
    BotKnowledge,
    BotModelInfo,
    BotOnboardingInfo,
    BotPromptInfo,
    BotSuggestReplyInfo,
    Coze,
    PluginIDList,
    SimpleBot,
    SuggestReplyMode,
    TokenAuth,
    WorkflowIDList,
)
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_simple_bot(bot_id: str) -> SimpleBot:
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


def mock_bot(bot_id) -> Bot:
    return Bot(
        bot_id=bot_id,
        name="name",
        description="description",
        icon_url="icon_url",
        create_time=0,
        update_time=0,
        version="version",
        logid=random_hex(10),
        owner_user_id=random_hex(10),
    )


def mock_create_bot(
    respx_mock,
) -> Bot:
    bot = mock_bot("bot_id")
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
    bot = mock_bot("bot_id")
    bot._raw_response = httpx.Response(
        200,
        json={"data": bot.model_dump()},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.post("/v1/bot/publish").mock(bot._raw_response)
    return bot


def mock_unpublish_bot(respx_mock, bot_id: str = "bot_id") -> None:
    respx_mock.post(f"/v1/bots/{bot_id}/unpublish").mock(
        httpx.Response(
            200,
            json={},
            headers={logid_key(): random_hex(10)},
        )
    )


def mock_retrieve_bot(respx_mock, use_api_version=1) -> Bot:
    bot_id = random_hex(10)
    bot = mock_bot(bot_id)
    bot._raw_response = httpx.Response(
        200,
        json={"data": bot.model_dump()},
        headers={logid_key(): random_hex(10)},
    )
    if use_api_version == 1:
        respx_mock.get("/v1/bot/get_online_info").mock(bot._raw_response)
    else:
        respx_mock.get(f"/v1/bots/{bot_id}").mock(bot._raw_response)
    return bot


def mock_list_bot(respx_mock, total_count, page, use_api_version=1):
    logid = random_hex(10)
    if use_api_version == 1:
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
                        "space_bots": [mock_simple_bot(f"id_{page}").model_dump()],
                        "total": total_count,
                    }
                },
                headers={logid_key(): logid},
            )
        )
    else:
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
    respx_mock.put("/v1/api_apps/app_id").mock(raw_response)
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
                    "has_more": True if page < total_count else False,
                }
            },
            headers={logid_key(): logid},
        )
    )
    return logid


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncBots:
    def test_sync_bot_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        bot = mock_create_bot(respx_mock)

        bot = coze.bots.create(space_id="space id", name="name")
        assert bot
        assert bot.response.logid == bot.response.logid
        assert bot.bot_id == bot.bot_id

    def test_sync_bot_create_with_advanced_params(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_bot = mock_create_bot(respx_mock)

        bot = coze.bots.create(
            space_id="space id",
            name="advanced bot",
            description="advanced bot description",
            prompt_info=BotPromptInfo(prompt="You are a helpful assistant."),
            onboarding_info=BotOnboardingInfo(
                prologue="Hello! How can I help you today?",
                suggested_questions=["What can you do?", "How to use this bot?"],
            ),
            knowledge=BotKnowledge(dataset_ids=["dataset_123", "dataset_456"], auto_call=True, search_strategy=0),
            suggest_reply_info=BotSuggestReplyInfo(reply_mode=SuggestReplyMode.ENABLE),
            model_info_config=BotModelInfo(model_id="doubao-pro-128k", temperature=0.7),
            plugin_id_list=PluginIDList(
                id_list=[
                    PluginIDList.PluginIDInfo(
                        plugin_id="7379227817307013129",  # 链接读取
                        api_id="7379227817307029513",  # LinkReaderPlugin
                    )
                ]
            ),
            workflow_id_list=WorkflowIDList(
                ids=[
                    WorkflowIDList.WorkflowIDInfo(
                        id="7527235627947917375"  # with_chat_role
                    )
                ]
            ),
        )
        assert bot
        assert bot.response.logid == mock_bot.response.logid
        assert bot.bot_id == mock_bot.bot_id

    def test_sync_bot_update(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_update_bot(respx_mock)

        res = coze.bots.update(bot_id="bot id", name="name")
        assert res
        assert res.response.logid is not None
        assert res.response.logid == mock_logid

    def test_sync_bot_publish(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_bot = mock_publish_bot(respx_mock)

        bot = coze.bots.publish(bot_id="bot id")
        assert bot
        assert bot.response.logid is not None
        assert bot.response.logid == mock_bot.response.logid
        assert bot.bot_id == mock_bot.bot_id

    def test_sync_bot_unpublish(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_unpublish_bot(respx_mock, bot_id="bot_id")

        resp = coze.bots.unpublish(bot_id="bot_id", connector_id="1024")
        assert resp

    def test_sync_bot_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        for use_api_version in [1, 2]:
            mock_bot = mock_retrieve_bot(respx_mock, use_api_version=use_api_version)

            bot = coze.bots.retrieve(bot_id=mock_bot.bot_id, use_api_version=use_api_version)
            assert bot
            assert bot.response.logid is not None
            assert bot.response.logid == mock_bot.response.logid
            assert bot.bot_id == mock_bot.bot_id

    def test_sync_bot_list_v1(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        for use_api_version in [1, 2]:
            space_id = random_hex(10)
            total = 10
            size = 1
            for idx in range(total):
                mock_list_bot(respx_mock, total_count=total, page=idx + 1, use_api_version=use_api_version)

            # no iter
            resp = coze.bots.list(space_id=space_id, page_num=1, page_size=1, use_api_version=use_api_version)
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
    async def test_async_bot_create(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_bot = mock_create_bot(respx_mock)

        bot = await coze.bots.create(space_id="space id", name="name")
        assert bot
        assert bot.response.logid is not None
        assert bot.response.logid == mock_bot.response.logid
        assert bot.bot_id == mock_bot.bot_id

    async def test_async_bot_create_with_advanced_params(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_bot = mock_create_bot(respx_mock)

        bot = await coze.bots.create(
            space_id="space id",
            name="advanced bot",
            description="advanced bot description",
            prompt_info=BotPromptInfo(prompt="You are a helpful assistant."),
            onboarding_info=BotOnboardingInfo(
                prologue="Hello! How can I help you today?",
                suggested_questions=["What can you do?", "How to use this bot?"],
            ),
            knowledge=BotKnowledge(dataset_ids=["dataset_123", "dataset_456"], auto_call=True, search_strategy=1),
            suggest_reply_info=BotSuggestReplyInfo(
                reply_mode=SuggestReplyMode.CUSTOMIZED, customized_prompt="Generate helpful follow-up questions"
            ),
            model_info_config=BotModelInfo(model_id="gpt-4", temperature=0.8, max_tokens=1500),
            plugin_id_list=PluginIDList(
                id_list=[
                    PluginIDList.PluginIDInfo(
                        plugin_id="7379227817307013129",  # 链接读取
                        api_id="7379227817307029513",  # LinkReaderPlugin
                    )
                ]
            ),
            workflow_id_list=WorkflowIDList(
                ids=[
                    WorkflowIDList.WorkflowIDInfo(
                        id="7527235627947917375"  # with_chat_role
                    )
                ]
            ),
        )
        assert bot
        assert bot.response.logid is not None
        assert bot.response.logid == mock_bot.response.logid
        assert bot.bot_id == mock_bot.bot_id

    async def test_async_bot_update(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_logid = mock_update_bot(respx_mock)

        res = await coze.bots.update(bot_id="bot id", name="name")
        assert res
        assert res.response.logid is not None
        assert res.response.logid == mock_logid

    async def test_async_bot_publish(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_bot = mock_publish_bot(respx_mock)

        bot = await coze.bots.publish(bot_id="bot id")
        assert bot
        assert bot.response.logid is not None
        assert bot.response.logid == mock_bot.response.logid
        assert bot.bot_id == mock_bot.bot_id

    async def test_async_bot_unpublish(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_unpublish_bot(respx_mock, bot_id="bot_id")

        resp = await coze.bots.unpublish(bot_id="bot_id", connector_id="1024")
        assert resp

    async def test_async_bot_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        for use_api_version in [1, 2]:
            mock_bot = mock_retrieve_bot(respx_mock, use_api_version=use_api_version)

            bot = await coze.bots.retrieve(bot_id=mock_bot.bot_id, use_api_version=use_api_version)
            assert bot
            assert bot.response.logid is not None
            assert bot.response.logid == mock_bot.response.logid
            assert bot.bot_id == mock_bot.bot_id

    async def test_async_bot_list(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        for use_api_version in [1, 2]:
            space_id = random_hex(10)
            total = 10
            size = 1
            for idx in range(total):
                mock_list_bot(respx_mock, total_count=total, page=idx + 1, use_api_version=use_api_version)

            # no iter
            resp = await coze.bots.list(space_id=space_id, page_num=1, page_size=1, use_api_version=use_api_version)
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
        assert ids == [f"id_{i + 1}" for i in range(total)]
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
        assert ids == [f"id_{i + 1}" for i in range(total)]
        total_result = 0
        async for page in resp.iter_pages():
            total_result += 1
            assert page
            assert len(page.items) == size
            app = page.items[0]
            assert app.id == f"id_{total_result}"
        assert total_result == total
