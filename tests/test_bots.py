import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Bot, Coze, SimpleBot, TokenAuth
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_simple_bot(bot_id: str) -> SimpleBot:
    """
    Create a SimpleBot instance with preset attributes and a random owner user ID.
    
    Parameters:
        bot_id (str): The unique identifier for the bot.
    
    Returns:
        SimpleBot: A SimpleBot object with the specified ID and fixed attribute values.
    """
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
    """
    Create a Bot instance with fixed attributes and random logid and owner user ID.
    
    Parameters:
        bot_id: The unique identifier for the bot.
    
    Returns:
        Bot: A Bot object with preset values and random logid and owner_user_id.
    """
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
    """
    Mocks the bot creation API endpoint and returns a Bot instance with a simulated response.
    
    Returns:
        Bot: The mocked Bot instance with an attached HTTP response.
    """
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
    """
    Mocks the bot publishing API endpoint and returns a Bot instance with a simulated response.
    
    Returns:
        Bot: The mocked Bot instance with a preset publish response.
    """
    bot = mock_bot("bot_id")
    bot._raw_response = httpx.Response(
        200,
        json={"data": bot.model_dump()},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.post("/v1/bot/publish").mock(bot._raw_response)
    return bot


def mock_retrieve_bot(respx_mock, use_api_version=1) -> Bot:
    """
    Mock the bot retrieval API endpoint for testing, supporting both v1 and v2 endpoints.
    
    Parameters:
        use_api_version (int): Specifies which API version to mock. Version 1 uses `/v1/bot/get_online_info`; version 2 uses `/v1/bots/{bot_id}`.
    
    Returns:
        Bot: A mocked Bot instance with a preset raw HTTP response.
    """
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
    """
    Mock the bot listing API endpoint for the specified API version and page, returning a paginated list of bots.
    
    Parameters:
        total_count (int): The total number of bots to include in the mocked response.
        page (int): The page index to mock in the response.
        use_api_version (int, optional): The API version to mock (1 or 2). Defaults to 1.
    
    Returns:
        str: The generated logid included in the mocked response headers.
    """
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
        """
        Tests synchronous retrieval of a bot using both API version 1 and 2, asserting that the returned bot matches the mocked bot and includes the expected logid.
        """
        coze = Coze(auth=TokenAuth(token="token"))

        for use_api_version in [1, 2]:
            mock_bot = mock_retrieve_bot(respx_mock, use_api_version=use_api_version)

            bot = coze.bots.retrieve(bot_id=mock_bot.bot_id, use_api_version=use_api_version)
            assert bot
            assert bot.response.logid is not None
            assert bot.response.logid == mock_bot.response.logid
            assert bot.bot_id == mock_bot.bot_id

    def test_sync_bots_list_v1(self, respx_mock):
        """
        Tests synchronous bot listing for both API versions, verifying pagination and correct retrieval of bot items and pages.
        """
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
        """
        Asynchronously tests bot retrieval for both API versions, asserting that the returned bot matches the mocked bot and includes the expected logid.
        """
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        for use_api_version in [1, 2]:
            mock_bot = mock_retrieve_bot(respx_mock, use_api_version=use_api_version)

            bot = await coze.bots.retrieve(bot_id=mock_bot.bot_id, use_api_version=use_api_version)
            assert bot
            assert bot.response.logid is not None
            assert bot.response.logid == mock_bot.response.logid
            assert bot.bot_id == mock_bot.bot_id

    async def test_async_bots_list(self, respx_mock):
        """
        Asynchronously tests the bot listing functionality for both API versions, verifying pagination and iteration over bots and pages.
        
        This test mocks paginated bot list responses for two API versions, then asserts that the asynchronous client correctly retrieves all bots and handles pagination flags when iterating over both individual bots and pages.
        """
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
