import httpx
import pytest

from cozepy import AsyncCoze, Coze, CreateRoomResult, TokenAuth
from cozepy.util import random_hex


def mock_create_speech(respx_mock):
    res = CreateRoomResult(token=random_hex(10), uid=random_hex(10), room_id=random_hex(10), app_id=random_hex(10))

    respx_mock.post("/v1/audio/speech").mock(
        httpx.Response(200, content="file content", headers={"content-type": "audio/mpeg"})
    )

    return res


@pytest.mark.respx(base_url="https://api.coze.com")
class TestAudioSpeech:
    def test_sync_speech_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_create_speech(respx_mock)

        res = coze.audio.speech.create(input=random_hex(10), voice_id=random_hex(10))
        assert res


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncAudioSpeech:
    async def test_async_speech_create(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        mock_create_speech(respx_mock)

        res = await coze.audio.speech.create(input=random_hex(10), voice_id=random_hex(10))
        assert res
