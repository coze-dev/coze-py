import asyncio
import json
import logging
import os

from cozepy import (
    AsyncCoze,
    AsyncWebsocketsAudioTranscriptionsCreateClient,
    AsyncWebsocketsAudioTranscriptionsEventHandler,
    AudioFormat,
    TokenAuth,
    TranscriptionsMessageUpdateEvent,
    setup_logging,
)
from examples.utils import get_coze_api_base, get_coze_api_token

coze_log = os.getenv("COZE_LOG")
if coze_log:
    setup_logging(logging.getLevelNamesMapping()[coze_log.upper()])
kwargs = json.loads(os.getenv("COZE_KWARGS") or "{}")


class AudioTranscriptionsEventHandlerSub(AsyncWebsocketsAudioTranscriptionsEventHandler):
    """
    Class is not required, you can also use Dict to set callback
    """

    async def on_closed(self, cli: "AsyncWebsocketsAudioTranscriptionsCreateClient"):
        print("Connection closed")

    async def on_error(self, cli: "AsyncWebsocketsAudioTranscriptionsCreateClient", e: Exception):
        print(f"Error occurred: {e}")

    async def on_transcriptions_message_update(
        self, cli: "AsyncWebsocketsAudioTranscriptionsCreateClient", event: TranscriptionsMessageUpdateEvent
    ):
        print("Received:", event.data.content)


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
        async for data in speech_stream():
            await client.append(data)
        await client.commit()
        await client.wait()


if __name__ == "__main__":
    asyncio.run(main())
