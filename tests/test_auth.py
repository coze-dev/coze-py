import time

import httpx
import pytest

from cozepy import (
    COZE_COM_BASE_URL,
    AsyncDeviceOAuthApp,
    AsyncJWTOAuthApp,
    AsyncPKCEOAuthApp,
    AsyncWebOAuthApp,
    CozePKCEAuthErrorType,
    DeviceAuthCode,
    DeviceOAuthApp,
    JWTAuth,
    JWTOAuthApp,
    OAuthToken,
    PKCEOAuthApp,
    Scope,
    WebOAuthApp,
)
from cozepy.util import random_hex

from .test_util import read_file


@pytest.mark.respx(base_url="https://api.coze.com")
class TestWebOAuthApp:
    def test_get_oauth_url(self, respx_mock):
        app = WebOAuthApp("client id", "client secret")

        url = app.get_oauth_url("https://example.com", "state")
        assert (
            "https://www.coze.com/api/permission/oauth2/authorize"
            "?response_type=code&"
            "client_id=client+id&"
            "redirect_uri=https%3A%2F%2Fexample.com&"
            "state=state"
        ) == url

        url = app.get_oauth_url("https://example.com", "state", workspace_id="this_is_id")
        assert (
            "https://www.coze.com/api/permission/oauth2/workspace_id/this_is_id/authorize"
            "?response_type=code&"
            "client_id=client+id&"
            "redirect_uri=https%3A%2F%2Fexample.com&"
            "state=state"
        ) == url

    def test_get_oauth_url_config_www_url(self, respx_mock):
        app = WebOAuthApp("client id", "client secret", www_base_url="https://example.com")

        url = app.get_oauth_url("https://example.com", "state")
        assert (
            "https://example.com/api/permission/oauth2/authorize"
            "?response_type=code&"
            "client_id=client+id&"
            "redirect_uri=https%3A%2F%2Fexample.com&"
            "state=state"
        ) == url

    def test_get_oauth_url_config_custom_api_base_url(self, respx_mock):
        app = WebOAuthApp("client id", "client secret", base_url="https://api.example.com")

        url = app.get_oauth_url("https://example.com", "state")
        assert (
            "https://api.example.com/api/permission/oauth2/authorize"
            "?response_type=code&"
            "client_id=client+id&"
            "redirect_uri=https%3A%2F%2Fexample.com&"
            "state=state"
        ) == url

    def test_get_access_token(self, respx_mock):
        app = WebOAuthApp("client id", "client secret")
        mock_token = random_hex(20)

        respx_mock.post("/api/permission/oauth2/token").mock(
            httpx.Response(
                200, content=OAuthToken(access_token=mock_token, expires_in=int(time.time())).model_dump_json()
            )
        )

        token = app.get_access_token("https://example.com", "code")

        assert token.access_token == mock_token

    def test_refresh_token(self, respx_mock):
        app = WebOAuthApp("client id", "client secret")
        mock_token = random_hex(20)
        respx_mock.post("/api/permission/oauth2/token").mock(
            httpx.Response(
                200, content=OAuthToken(access_token=mock_token, expires_in=int(time.time())).model_dump_json()
            )
        )

        token = app.refresh_access_token("refresh token")
        assert token.access_token == mock_token


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncWebOAuthApp:
    async def test_get_oauth_url(self, respx_mock):
        app = AsyncWebOAuthApp("client id", "client secret")

        url = app.get_oauth_url("https://example.com", "state")
        assert (
            "https://www.coze.com/api/permission/oauth2/authorize"
            "?response_type=code&"
            "client_id=client+id&"
            "redirect_uri=https%3A%2F%2Fexample.com&"
            "state=state"
        ) == url

        url = app.get_oauth_url("https://example.com", "state", workspace_id="this_is_id")
        assert (
            "https://www.coze.com/api/permission/oauth2/workspace_id/this_is_id/authorize"
            "?response_type=code&"
            "client_id=client+id&"
            "redirect_uri=https%3A%2F%2Fexample.com&"
            "state=state"
        ) == url

    async def test_get_oauth_url_config_www_url(self, respx_mock):
        app = AsyncWebOAuthApp("client id", "client secret", www_base_url="https://example.com")

        url = app.get_oauth_url("https://example.com", "state")
        assert (
            "https://example.com/api/permission/oauth2/authorize"
            "?response_type=code&"
            "client_id=client+id&"
            "redirect_uri=https%3A%2F%2Fexample.com&"
            "state=state"
        ) == url

    async def test_get_oauth_url_config_custom_api_base_url(self, respx_mock):
        app = AsyncWebOAuthApp("client id", "client secret", base_url="https://api.example.com")

        url = app.get_oauth_url("https://example.com", "state")
        assert (
            "https://api.example.com/api/permission/oauth2/authorize"
            "?response_type=code&"
            "client_id=client+id&"
            "redirect_uri=https%3A%2F%2Fexample.com&"
            "state=state"
        ) == url

    async def test_get_access_token(self, respx_mock):
        app = AsyncWebOAuthApp("client id", "client secret")
        mock_token = random_hex(20)

        respx_mock.post("/api/permission/oauth2/token").mock(
            httpx.Response(
                200, content=OAuthToken(access_token=mock_token, expires_in=int(time.time())).model_dump_json()
            )
        )

        token = await app.get_access_token("https://example.com", "code")

        assert token.access_token == mock_token

    async def test_refresh_token(self, respx_mock):
        app = AsyncWebOAuthApp("client id", "client secret")
        mock_token = random_hex(20)
        respx_mock.post("/api/permission/oauth2/token").mock(
            httpx.Response(
                200, content=OAuthToken(access_token=mock_token, expires_in=int(time.time())).model_dump_json()
            )
        )

        token = await app.refresh_access_token("refresh token")
        assert token.access_token == mock_token


@pytest.mark.respx(base_url="https://api.coze.com")
class TestJWTOAuthApp:
    def test_jwt_auth(self, respx_mock):
        private_key = read_file("testdata/private_key.pem")
        mock_token = random_hex(20)
        respx_mock.post("/api/permission/oauth2/token").mock(
            httpx.Response(
                200, content=OAuthToken(access_token=mock_token, expires_in=int(time.time()) + 100).model_dump_json()
            )
        )

        auth = JWTAuth("client id", private_key, "public key id")

        assert "Bearer" == auth.token_type
        assert mock_token == auth.token
        assert mock_token == auth.token  # get from cache

    def test_get_access_token(self, respx_mock):
        private_key = read_file("testdata/private_key.pem")
        app = JWTOAuthApp("client id", private_key, "public key id")
        mock_token = random_hex(20)
        respx_mock.post("/api/permission/oauth2/token").mock(
            httpx.Response(
                200, content=OAuthToken(access_token=mock_token, expires_in=int(time.time())).model_dump_json()
            )
        )

        token = app.get_access_token(100, scope=Scope.build_bot_chat(["bot id"]), session_name="session_name")
        assert token.access_token == mock_token


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncJWTOAuthApp:
    async def test_get_access_token(self, respx_mock):
        private_key = read_file("testdata/private_key.pem")
        app = AsyncJWTOAuthApp("client id", private_key, "public key id")
        mock_token = random_hex(20)
        respx_mock.post("/api/permission/oauth2/token").mock(
            httpx.Response(
                200, content=OAuthToken(access_token=mock_token, expires_in=int(time.time())).model_dump_json()
            )
        )

        token = await app.get_access_token(100, scope=Scope.build_bot_chat(["bot id"]))
        assert token.access_token == mock_token


@pytest.mark.respx(base_url="https://api.coze.com")
class TestPKCEOAuthApp:
    def test_get_oauth_url(self, respx_mock):
        app = PKCEOAuthApp("client id")

        url = app.get_oauth_url("https://example.com", "code_verifier", "S256", state="state")
        assert (
            "https://www.coze.com/api/permission/oauth2/authorize?"
            "response_type=code&client_id=client+id&"
            "redirect_uri=https%3A%2F%2Fexample.com&state=state&"
            "code_challenge=73oehA2tBul5grZPhXUGQwNAjxh69zNES8bu2bVD0EM&code_challenge_method=S256"
        ) == url

        url = app.get_oauth_url(
            "https://example.com", "code_verifier", "S256", state="state", workspace_id="this_is_id"
        )
        assert (
            "https://www.coze.com/api/permission/oauth2/workspace_id/this_is_id/authorize?"
            "response_type=code&client_id=client+id&"
            "redirect_uri=https%3A%2F%2Fexample.com&state=state&"
            "code_challenge=73oehA2tBul5grZPhXUGQwNAjxh69zNES8bu2bVD0EM&code_challenge_method=S256"
        ) == url

    def test_get_access_token(self, respx_mock):
        app = PKCEOAuthApp("client id")
        mock_token = random_hex(20)

        respx_mock.post("/api/permission/oauth2/token").mock(
            httpx.Response(
                200, content=OAuthToken(access_token=mock_token, expires_in=int(time.time())).model_dump_json()
            )
        )

        token = app.get_access_token("https://example.com", "code", "code_verifier")

        assert token.access_token == mock_token

    def test_refresh_token(self, respx_mock):
        app = PKCEOAuthApp("client id")
        mock_token = random_hex(20)
        respx_mock.post("/api/permission/oauth2/token").mock(
            httpx.Response(
                200, content=OAuthToken(access_token=mock_token, expires_in=int(time.time())).model_dump_json()
            )
        )

        token = app.refresh_access_token("refresh token")
        assert token.access_token == mock_token


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncPKCEOAuthApp:
    async def test_get_oauth_url(self, respx_mock):
        app = AsyncPKCEOAuthApp("client id")

        url = app.get_oauth_url("https://example.com", "code_verifier", "S256", state="state")
        assert (
            "https://www.coze.com/api/permission/oauth2/authorize?"
            "response_type=code&client_id=client+id&"
            "redirect_uri=https%3A%2F%2Fexample.com&state=state&"
            "code_challenge=73oehA2tBul5grZPhXUGQwNAjxh69zNES8bu2bVD0EM&code_challenge_method=S256"
        ) == url

        url = app.get_oauth_url(
            "https://example.com", "code_verifier", "S256", workspace_id="this_is_id", state="state"
        )
        assert (
            "https://www.coze.com/api/permission/oauth2/workspace_id/this_is_id/authorize?"
            "response_type=code&client_id=client+id&"
            "redirect_uri=https%3A%2F%2Fexample.com&state=state&"
            "code_challenge=73oehA2tBul5grZPhXUGQwNAjxh69zNES8bu2bVD0EM&code_challenge_method=S256"
        ) == url

    async def test_get_access_token(self, respx_mock):
        app = AsyncPKCEOAuthApp("client id")
        mock_token = random_hex(20)

        respx_mock.post("/api/permission/oauth2/token").mock(
            httpx.Response(
                200, content=OAuthToken(access_token=mock_token, expires_in=int(time.time())).model_dump_json()
            )
        )

        token = await app.get_access_token("https://example.com", "code", "code_verifier")

        assert token.access_token == mock_token

    async def test_refresh_token(self, respx_mock):
        app = AsyncPKCEOAuthApp("client id")
        mock_token = random_hex(20)
        respx_mock.post("/api/permission/oauth2/token").mock(
            httpx.Response(
                200, content=OAuthToken(access_token=mock_token, expires_in=int(time.time())).model_dump_json()
            )
        )

        token = await app.refresh_access_token("refresh token")
        assert token.access_token == mock_token


@pytest.mark.respx(base_url="https://api.coze.com")
class TestDeviceOAuthApp:
    def test_get_device_code(self, respx_mock):
        app = DeviceOAuthApp("client id")
        mock_code = random_hex(20)

        respx_mock.post("/api/permission/oauth2/device/code").mock(
            httpx.Response(
                200,
                content=DeviceAuthCode(
                    device_code=mock_code,
                    user_code="user_code",
                    verification_uri=COZE_COM_BASE_URL,
                    interval=5,
                    expires_in=int(time.time()),
                ).model_dump_json(),
            )
        )

        device_code = app.get_device_code()
        assert device_code.device_code == mock_code

    def test_workspace_get_device_code(self, respx_mock):
        app = DeviceOAuthApp("client id")
        mock_code = random_hex(20)

        respx_mock.post("/api/permission/oauth2/workspace_id/this_is_id/device/code").mock(
            httpx.Response(
                200,
                content=DeviceAuthCode(
                    device_code=mock_code,
                    user_code="user_code",
                    verification_uri=COZE_COM_BASE_URL,
                    interval=5,
                    expires_in=int(time.time()),
                ).model_dump_json(),
            )
        )

        device_code = app.get_device_code(workspace_id="this_is_id")
        assert device_code.device_code == mock_code

    def test_get_access_token(self, respx_mock):
        app = DeviceOAuthApp("client id")
        mock_token = random_hex(20)

        respx_mock.post("/api/permission/oauth2/token").mock(
            httpx.Response(
                200, content=OAuthToken(access_token=mock_token, expires_in=int(time.time())).model_dump_json()
            )
        )

        token = app.get_access_token("https://example.com", False)

        assert token.access_token == mock_token

    def test_get_access_token_poll(self, respx_mock):
        app = DeviceOAuthApp("client id")
        mock_token = random_hex(20)

        respx_mock.post("/api/permission/oauth2/token").mock(
            httpx.Response(200, json={"error_code": CozePKCEAuthErrorType.AUTHORIZATION_PENDING})
        ).mock(
            httpx.Response(
                200, content=OAuthToken(access_token=mock_token, expires_in=int(time.time())).model_dump_json()
            )
        )
        token = app.get_access_token("https://example.com", True)

        assert token.access_token == mock_token

    def test_refresh_token(self, respx_mock):
        app = DeviceOAuthApp("client id")
        mock_token = random_hex(20)
        respx_mock.post("/api/permission/oauth2/token").mock(
            httpx.Response(
                200, content=OAuthToken(access_token=mock_token, expires_in=int(time.time())).model_dump_json()
            )
        )

        token = app.refresh_access_token("refresh token")
        assert token.access_token == mock_token


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncDeviceOAuthApp:
    async def test_get_device_code(self, respx_mock):
        app = AsyncDeviceOAuthApp("client id")
        mock_code = random_hex(20)

        respx_mock.post("/api/permission/oauth2/device/code").mock(
            httpx.Response(
                200,
                content=DeviceAuthCode(
                    device_code=mock_code,
                    user_code="user_code",
                    verification_uri=COZE_COM_BASE_URL,
                    interval=5,
                    expires_in=int(time.time()),
                ).model_dump_json(),
            )
        )

        device_code = await app.get_device_code()
        assert device_code.device_code == mock_code

    async def test_workspace_get_device_code(self, respx_mock):
        app = AsyncDeviceOAuthApp("client id")
        mock_code = random_hex(20)

        respx_mock.post("/api/permission/oauth2/workspace_id/this_is_id/device/code").mock(
            httpx.Response(
                200,
                content=DeviceAuthCode(
                    device_code=mock_code,
                    user_code="user_code",
                    verification_uri=COZE_COM_BASE_URL,
                    interval=5,
                    expires_in=int(time.time()),
                ).model_dump_json(),
            )
        )

        device_code = await app.get_device_code(workspace_id="this_is_id")
        assert device_code.device_code == mock_code

    async def test_get_access_token(self, respx_mock):
        app = AsyncDeviceOAuthApp("client id")
        mock_token = random_hex(20)

        respx_mock.post("/api/permission/oauth2/token").mock(
            httpx.Response(
                200, content=OAuthToken(access_token=mock_token, expires_in=int(time.time())).model_dump_json()
            )
        )

        token = await app.get_access_token("https://example.com", False)

        assert token.access_token == mock_token

    async def test_get_access_token_poll(self, respx_mock):
        app = AsyncDeviceOAuthApp("client id")
        mock_token = random_hex(20)

        respx_mock.post("/api/permission/oauth2/token").mock(
            httpx.Response(200, json={"error_code": CozePKCEAuthErrorType.AUTHORIZATION_PENDING})
        ).mock(
            httpx.Response(
                200, content=OAuthToken(access_token=mock_token, expires_in=int(time.time())).model_dump_json()
            )
        )
        token = await app.get_access_token("https://example.com", True)

        assert token.access_token == mock_token

    async def test_refresh_token(self, respx_mock):
        app = AsyncDeviceOAuthApp("client id")
        mock_token = random_hex(20)
        respx_mock.post("/api/permission/oauth2/token").mock(
            httpx.Response(
                200, content=OAuthToken(access_token=mock_token, expires_in=int(time.time())).model_dump_json()
            )
        )

        token = await app.refresh_access_token("refresh token")
        assert token.access_token == mock_token
