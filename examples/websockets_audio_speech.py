import asyncio
import json
import logging
import os
from typing import Optional

from cozepy import (
    COZE_CN_BASE_URL,
    AsyncCoze,
    AsyncTokenAuth,
    AsyncWebsocketsAudioSpeechClient,
    AsyncWebsocketsAudioSpeechEventHandler,
    DeviceOAuthApp,
    InputTextBufferAppendEvent,
    InputTextBufferCompletedEvent,
    SpeechAudioCompletedEvent,
    SpeechAudioUpdateEvent,
    setup_logging,
)
from cozepy.log import log_info
from cozepy.util import write_pcm_to_wav_file


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


class AsyncWebsocketsAudioSpeechEventHandlerSub(AsyncWebsocketsAudioSpeechEventHandler):
    """
    Class is not required, you can also use Dict to set callback
    """

    delta = []

    async def on_closed(self, cli: "AsyncWebsocketsAudioSpeechClient"):
        log_info("[examples] connect closed")

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
        auth=AsyncTokenAuth(coze_api_token),
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
