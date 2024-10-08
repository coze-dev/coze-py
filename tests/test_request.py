import httpx
import pytest

from cozepy import CozeAPIError, CozePKCEAuthError
from cozepy.model import CozeModel
from cozepy.request import Requester


class ModelForTest(CozeModel):
    id: str


class DebugModelForTest(CozeModel):
    debug_url: str
    data: str


@pytest.mark.respx(base_url="https://api.coze.com")
class TestRequester:
    def test_code_msg(self, respx_mock):
        respx_mock.post("/api/test").mock(
            httpx.Response(200, json={"code": 100, "msg": "request failed"}, headers={"x-tt-logid": "mock-logid"})
        )

        with pytest.raises(CozeAPIError, match="code: 100, msg: request failed, logid: mock-logid"):
            Requester().request("post", "https://api.coze.com/api/test", ModelForTest)

    def test_auth_slow_down(self, respx_mock):
        respx_mock.post("/api/test").mock(
            httpx.Response(
                200,
                json={
                    "error_code": "slow_down",
                },
                headers={"x-tt-logid": "mock-logid"},
            )
        )

        with pytest.raises(CozePKCEAuthError, match="pkce auth error: slow_down"):
            Requester().request("post", "https://api.coze.com/api/test", ModelForTest)

    def test_error_message(self, respx_mock):
        respx_mock.post("/api/test").mock(
            httpx.Response(
                200,
                json={
                    "error_message": "error_message",
                },
                headers={"x-tt-logid": "mock-logid"},
            )
        )

        with pytest.raises(CozeAPIError, match="msg: error_message, logid: mock-logid"):
            Requester().request("post", "https://api.coze.com/api/test", ModelForTest)

    def test_debug_url(self, respx_mock):
        respx_mock.post("/api/test").mock(
            httpx.Response(
                200,
                json={
                    "debug_url": "debug_url",
                    "data": "data",
                },
                headers={"x-tt-logid": "mock-logid"},
            )
        )

        Requester().request("post", "https://api.coze.com/api/test", DebugModelForTest)


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncRequester:
    async def test_code_msg(self, respx_mock):
        respx_mock.post("/api/test").mock(
            httpx.Response(200, json={"code": 100, "msg": "request failed"}, headers={"x-tt-logid": "mock-logid"})
        )

        with pytest.raises(CozeAPIError, match="code: 100, msg: request failed, logid: mock-logid"):
            await Requester().arequest("post", "https://api.coze.com/api/test", ModelForTest)

    async def test_auth_slow_down(self, respx_mock):
        respx_mock.post("/api/test").mock(
            httpx.Response(
                200,
                json={
                    "error_code": "slow_down",
                },
                headers={"x-tt-logid": "mock-logid"},
            )
        )

        with pytest.raises(CozePKCEAuthError, match="pkce auth error: slow_down"):
            await Requester().arequest("post", "https://api.coze.com/api/test", ModelForTest)

    async def test_error_message(self, respx_mock):
        respx_mock.post("/api/test").mock(
            httpx.Response(
                200,
                json={
                    "error_message": "error_message",
                },
                headers={"x-tt-logid": "mock-logid"},
            )
        )

        with pytest.raises(CozeAPIError, match="msg: error_message, logid: mock-logid"):
            await Requester().arequest("post", "https://api.coze.com/api/test", ModelForTest)

    async def test_debug_url(self, respx_mock):
        respx_mock.post("/api/test").mock(
            httpx.Response(
                200,
                json={
                    "debug_url": "debug_url",
                    "data": "data",
                },
                headers={"x-tt-logid": "mock-logid"},
            )
        )

        await Requester().arequest("post", "https://api.coze.com/api/test", DebugModelForTest)
