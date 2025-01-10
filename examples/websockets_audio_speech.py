import asyncio
import json
import os

from cozepy import (
    AsyncCoze,
    AsyncWebsocketsAudioSpeechClient,
    AsyncWebsocketsAudioSpeechEventHandler,
    InputTextBufferAppendEvent,
    InputTextBufferCompletedEvent,
    SpeechAudioCompletedEvent,
    SpeechAudioUpdateEvent,
    TokenAuth,
)
from cozepy.log import log_info
from cozepy.util import write_pcm_to_wav_file
from examples.utils import get_coze_api_base, get_coze_api_token, setup_examples_logger

setup_examples_logger()

kwargs = json.loads(os.getenv("COZE_KWARGS") or "{}")


# todo review
class AsyncWebsocketsAudioSpeechEventHandlerSub(AsyncWebsocketsAudioSpeechEventHandler):
    """
    Class is not required, you can also use Dict to set callback
    """

    delta = []

    async def on_input_text_buffer_completed(
        self, cli: "AsyncWebsocketsAudioSpeechClient", event: InputTextBufferCompletedEvent
    ):
        log_info("[examples] Input text buffer completed")

    async def on_speech_audio_update(self, cli: AsyncWebsocketsAudioSpeechClient, event: SpeechAudioUpdateEvent):
        self.delta.append(event.data.delta)

    async def on_error(self, cli: AsyncWebsocketsAudioSpeechClient, e: Exception):
        log_info("[examples] Error occurred: %s", e)

    async def on_speech_audio_completed(
        self, cli: "AsyncWebsocketsAudioSpeechClient", event: SpeechAudioCompletedEvent
    ):
        log_info("[examples] Saving audio data to output.wav")
        write_pcm_to_wav_file(b"".join(self.delta), "output.wav")
        self.delta = []


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
        await client.input_text_buffer_append(
            InputTextBufferAppendEvent.Data.model_validate(
                {
                    "delta": text,
                }
            )
        )
        await client.input_text_buffer_complete()
        await client.wait()


if __name__ == "__main__":
    asyncio.run(main())
