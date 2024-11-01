import time

import httpx
import pytest

from cozepy import AsyncCoze, Coze, CreateRoomResult, TokenAuth, Voice
from cozepy.util import random_hex


def mock_list_voices(respx_mock):
    res = CreateRoomResult(token=random_hex(10), uid=random_hex(10), room_id=random_hex(10), app_id=random_hex(10))

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
        )
    )

    return res


@pytest.mark.respx(base_url="https://api.coze.com")
class TestAudioVoices:
    def test_sync_voices_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_list_voices(respx_mock)

        voices = coze.audio.voices.list()
        voices = [i for i in voices]
        assert voices
        assert len(voices) == 1


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncAudioVoices:
    async def test_async_voices_list(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        mock_list_voices(respx_mock)

        voices = await coze.audio.voices.list()
        voices = [i async for i in voices]
        assert voices
        assert len(voices) == 1
