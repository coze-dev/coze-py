import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Coze, TokenAuth, User
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_retrieve_users_me(
    respx_mock,
) -> User:
    user = User(
        user_id="user_id",
        user_name=random_hex(10),
        nick_name=random_hex(10),
        avatar_url=random_hex(10),
    )
    user._raw_response = httpx.Response(
        200,
        json={"data": user.model_dump()},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.get("/v1/users/me").mock(user._raw_response)
    return user


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncUsers:
    def test_sync_users_retrieve_me(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_user = mock_retrieve_users_me(respx_mock)

        user = coze.users.me()
        assert user
        assert user.response.logid == mock_user.response.logid
        assert user.user_id == mock_user.user_id


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncUsers:
    async def test_async_users_retrieve_me(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_user = mock_retrieve_users_me(respx_mock)

        user = await coze.users.me()
        assert user
        assert user.response.logid == mock_user.response.logid
        assert user.user_id == mock_user.user_id
