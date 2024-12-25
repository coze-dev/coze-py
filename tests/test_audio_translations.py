import httpx
import pytest

from cozepy import AsyncCoze, Coze, TokenAuth
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_create_translation(respx_mock):
    logid = random_hex(10)
    raw_response = httpx.Response(
        200,
        json={
            "text": "text",
        },
        headers={
            "content-type": "audio/mpeg",
            logid_key(): logid,
        },
    )

    respx_mock.post("/v1/audio/translations").mock(raw_response)

    return logid


@pytest.mark.respx(base_url="https://api.coze.com")
class TestAudioTranslation:
    def test_sync_translation_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_create_translation(respx_mock)

        res = coze.audio.translations.create(file=("filename", "content"))
        assert res
        assert res.response.logid is not None
        assert res.response.logid == mock_logid


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncAudioTranslation:
    async def test_async_translation_create(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        mock_logid = mock_create_translation(respx_mock)

        res = await coze.audio.translations.create(file=("filename", "content"))
        assert res
        assert res.response.logid == mock_logid
