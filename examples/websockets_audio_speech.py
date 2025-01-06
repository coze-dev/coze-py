import asyncio
import json
import logging
import os

from cozepy import (
    AsyncCoze,
    AsyncWebsocketsAudioSpeechCreateClient,
    AsyncWebsocketsAudioSpeechEventHandler,
    SpeechAudioUpdateEvent,
    TokenAuth,
    setup_logging,
)
from cozepy.util import write_pcm_to_wav_file
from examples.utils import get_coze_api_base, get_coze_api_token

coze_log = os.getenv("COZE_LOG")
if coze_log:
    setup_logging(logging.getLevelNamesMapping()[coze_log.upper()])

kwargs = json.loads(os.getenv("COZE_KWARGS") or "{}")


class AsyncWebsocketsAudioSpeechEventHandlerSub(AsyncWebsocketsAudioSpeechEventHandler):
    delta = []

    async def on_speech_audio_update(self, cli: AsyncWebsocketsAudioSpeechCreateClient, event: SpeechAudioUpdateEvent):
        self.delta.append(event.data.delta)

    async def on_error(self, cli: AsyncWebsocketsAudioSpeechCreateClient, e: Exception):
        print(f"Error occurred: {e}")

    async def on_closed(self, cli: AsyncWebsocketsAudioSpeechCreateClient):
        print("Speech connection closed, saving audio data to output.wav")
        audio_data = b"".join(self.delta)
        write_pcm_to_wav_file(audio_data, "output.wav")


async def main():
    coze_api_token = get_coze_api_token()
    coze_api_base = get_coze_api_base()

    # Initialize Coze client
    coze = AsyncCoze(
        auth=TokenAuth(coze_api_token),
        base_url=coze_api_base,
    )

    speech = coze.websockets.audio.speech.create(
        on_event=AsyncWebsocketsAudioSpeechEventHandlerSub(),
        **kwargs,
    )

    # Text to be converted to speech
    text = "你今天好吗? 今天天气不错呀"

    async with speech() as client:
        await client.append(text)
        await client.commit()
        await client.wait()


if __name__ == "__main__":
    asyncio.run(main())
