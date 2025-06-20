import time

import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, AudioFormat, Coze, TokenAuth, Voice, VoiceModelType, VoiceState
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_voice() -> Voice:
    return Voice(
        voice_id="voice_id",
        name="name",
        is_system_voice=False,
        language_code="language_code",
        language_name="language_name",
        preview_text="preview_text",
        preview_audio="preview_audio",
        available_training_times=1,
        create_time=int(time.time()),
        update_time=int(time.time()),
        model_type=VoiceModelType.BIG,
        state=VoiceState.INIT,
    )


def mock_list_voices(respx_mock) -> str:
    logid = random_hex(10)
    raw_response = httpx.Response(
        200,
        json={
            "data": {
                "voice_list": [mock_voice().model_dump()],
                "has_more": False,
            }
        },
        headers={logid_key(): logid},
    )

    respx_mock.get("/v1/audio/voices").mock(raw_response)

    return logid


def mock_clone_voice(respx_mock) -> Voice:
    voice = mock_voice()
    voice._raw_response = httpx.Response(
        200,
        json={"data": voice.model_dump()},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.post("/v1/audio/voices/clone").mock(voice._raw_response)
    return voice


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncAudioVoices:
    def test_sync_voices_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_list_voices(respx_mock)

        voices = coze.audio.voices.list()
        assert voices.response.logid == mock_logid

        voices = [i for i in voices]
        assert voices
        assert len(voices) == 1

    def test_clone_voice(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_voice = mock_clone_voice(respx_mock)

        voice = coze.audio.voices.clone(voice_name="voice_name", file=("name", "content"), audio_format=AudioFormat.MP3)
        assert voice.response.logid == mock_voice.response.logid


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncAudioVoices:
    async def test_async_voices_list(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_logid = mock_list_voices(respx_mock)

        voices = await coze.audio.voices.list()
        assert voices.response.logid == mock_logid

        voices = [i async for i in voices]
        assert voices
        assert len(voices) == 1

    async def test_async_clone_voice(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_voice = mock_clone_voice(respx_mock)

        voice = await coze.audio.voices.clone(
            voice_name="voice_name", file=("name", "content"), audio_format=AudioFormat.MP3
        )
        assert voice.response.logid == mock_voice.response.logid
