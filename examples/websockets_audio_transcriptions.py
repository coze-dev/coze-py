import asyncio
import json
import logging
import os

from cozepy import (
    AsyncCoze,
    AsyncWebsocketsAudioTranscriptionsClient,
    AsyncWebsocketsAudioTranscriptionsEventHandler,
    AudioFormat,
    InputAudioBufferAppendEvent,
    InputAudioBufferCompletedEvent,
    TokenAuth,
    TranscriptionsMessageUpdateEvent,
    setup_logging,
)
from cozepy.log import log_info
from examples.utils import get_coze_api_base, get_coze_api_token

coze_log = os.getenv("COZE_LOG")
if coze_log:
    setup_logging(logging.getLevelNamesMapping()[coze_log.upper()])
kwargs = json.loads(os.getenv("COZE_KWARGS") or "{}")


class AudioTranscriptionsEventHandlerSub(AsyncWebsocketsAudioTranscriptionsEventHandler):
    """
    Class is not required, you can also use Dict to set callback
    """

    async def on_closed(self, cli: "AsyncWebsocketsAudioTranscriptionsClient"):
        log_info("[examples] Connect closed")

    async def on_error(self, cli: "AsyncWebsocketsAudioTranscriptionsClient", e: Exception):
        log_info("[examples] Error occurred: %s", e)

    async def on_transcriptions_message_update(
        self, cli: "AsyncWebsocketsAudioTranscriptionsClient", event: TranscriptionsMessageUpdateEvent
    ):
        log_info("[examples] Received: %s", event.data.content)

    async def on_input_audio_buffer_completed(
        self, cli: "AsyncWebsocketsAudioTranscriptionsClient", event: InputAudioBufferCompletedEvent
    ):
        log_info("[examples] Input audio buffer completed")


def wrap_coze_speech_to_iterator(coze: AsyncCoze, text: str):
    async def iterator():
        voices = await coze.audio.voices.list(**kwargs)
        content = await coze.audio.speech.create(
            input=text,
            voice_id=voices.items[0].voice_id,
            response_format=AudioFormat.WAV,
            sample_rate=24000,
            **kwargs,
        )
        for data in content._raw_response.iter_bytes(chunk_size=1024):
            yield data

    return iterator


async def main():
    coze_api_token = get_coze_api_token()
    coze_api_base = get_coze_api_base()

    # Initialize Coze client
    coze = AsyncCoze(
        auth=TokenAuth(coze_api_token),
        base_url=coze_api_base,
    )
    # Initialize Audio
    speech_stream = wrap_coze_speech_to_iterator(coze, "你今天好吗? 今天天气不错呀")

    transcriptions = coze.websockets.audio.transcriptions.create(
        on_event=AudioTranscriptionsEventHandlerSub(),
        **kwargs,
    )

    # Create and connect WebSocket client
    async with transcriptions() as client:
        async for delta in speech_stream():
            await client.input_audio_buffer_append(
                InputAudioBufferAppendEvent.Data.model_validate(
                    {
                        "delta": delta,
                    }
                )
            )
        await client.input_audio_buffer_complete()
        await client.wait()


if __name__ == "__main__":
    asyncio.run(main())
