import asyncio
import json
import logging
import os
from typing import Optional

from cozepy import (
    COZE_CN_BASE_URL,
    AsyncCoze,
    AsyncTokenAuth,
    AsyncWebsocketsAudioTranscriptionsClient,
    AsyncWebsocketsAudioTranscriptionsEventHandler,
    AudioFormat,
    DeviceOAuthApp,
    InputAudioBufferAppendEvent,
    InputAudioBufferCompletedEvent,
    TranscriptionsMessageUpdateEvent,
    setup_logging,
)
from cozepy.log import log_info


def get_coze_api_base() -> str:
    # The default access is api.coze.cn, but if you need to access api.coze.com,
    # please use base_url to configure the api endpoint to access
    coze_api_base = os.getenv("COZE_API_BASE")
    if coze_api_base:
        return coze_api_base

    return COZE_CN_BASE_URL  # default


def get_coze_api_token(workspace_id: Optional[str] = None) -> str:
    # Get an access_token through personal access token or oauth.
    coze_api_token = os.getenv("COZE_API_TOKEN")
    if coze_api_token:
        return coze_api_token

    coze_api_base = get_coze_api_base()

    device_oauth_app = DeviceOAuthApp(client_id="57294420732781205987760324720643.app.coze", base_url=coze_api_base)
    device_code = device_oauth_app.get_device_code(workspace_id)
    print(f"Please Open: {device_code.verification_url} to get the access token")
    return device_oauth_app.get_access_token(device_code=device_code.device_code, poll=True).access_token


def setup_examples_logger():
    coze_log = os.getenv("COZE_LOG")
    if coze_log:
        setup_logging(logging.getLevelNamesMapping().get(coze_log.upper(), logging.INFO))


setup_examples_logger()

kwargs = json.loads(os.getenv("COZE_KWARGS") or "{}")


class AudioTranscriptionsEventHandlerSub(AsyncWebsocketsAudioTranscriptionsEventHandler):
    """
    Class is not required, you can also use Dict to set callback
    """

    async def on_closed(self, cli: "AsyncWebsocketsAudioTranscriptionsClient"):
        log_info("[examples] connect closed")

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
        auth=AsyncTokenAuth(coze_api_token),
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
