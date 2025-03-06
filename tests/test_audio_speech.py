import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Coze, TokenAuth
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_create_speech(respx_mock):
    logid = random_hex(10)
    raw_response = httpx.Response(
        200,
        content="file content",
        headers={
            "content-type": "audio/mpeg",
            logid_key(): logid,
        },
    )

    respx_mock.post("/v1/audio/speech").mock(raw_response)

    return logid


@pytest.mark.respx(base_url="https://api.coze.com")
class TestAudioSpeech:
    def test_sync_speech_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_create_speech(respx_mock)

        res = coze.audio.speech.create(input=random_hex(10), voice_id=random_hex(10), speed=1.5, sample_rate=32000)
        assert res
        assert res.response.logid is not None
        assert res.response.logid == mock_logid


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncAudioSpeech:
    async def test_async_speech_create(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_logid = mock_create_speech(respx_mock)

        res = await coze.audio.speech.create(input=random_hex(10), voice_id=random_hex(10))
        assert res
        assert res.response.logid is not None
        assert res.response.logid == mock_logid
