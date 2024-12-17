import time

import httpx
import pytest

from cozepy import AsyncCoze, Coze, TokenAuth, Voice
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_list_voices(respx_mock):
    logid = random_hex(10)
    respx_mock.get("/v1/audio/voices").mock(
        httpx.Response(
            200,
            json={
                "data": {
                    "voice_list": [
                        Voice(
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
                        ).model_dump()
                    ],
                    "has_more": False,
                }
            },
            headers={logid_key(): logid},
        )
    )

    return logid


@pytest.mark.respx(base_url="https://api.coze.com")
class TestAudioVoices:
    def test_sync_voices_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_list_voices(respx_mock)

        voices = coze.audio.voices.list()
        assert voices.logid is not None
        assert voices.logid == mock_logid

        voices = [i for i in voices]
        assert voices
        assert len(voices) == 1


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncAudioVoices:
    async def test_async_voices_list(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        mock_logid = mock_list_voices(respx_mock)

        voices = await coze.audio.voices.list()
        assert voices.logid is not None
        assert voices.logid == mock_logid

        voices = [i async for i in voices]
        assert voices
        assert len(voices) == 1
