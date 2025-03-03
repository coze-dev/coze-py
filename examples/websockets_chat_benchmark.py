import asyncio
import json
import logging
import os
import time
from time import sleep
from typing import List, Optional

from cozepy import (
    COZE_CN_BASE_URL,
    AsyncCoze,
    AsyncWebsocketsChatClient,
    AsyncWebsocketsChatEventHandler,
    AudioFormat,
    ConversationAudioDeltaEvent,
    ConversationAudioTranscriptCompletedEvent,
    ConversationChatCreatedEvent,
    ConversationMessageDeltaEvent,
    DeviceOAuthApp,
    InputAudioBufferAppendEvent,
    TokenAuth,
    WebsocketsEventType,
    setup_logging,
)
from cozepy.log import log_info


def get_coze_api_base() -> str:
    # The default access is api.coze.com, but if you need to access api.coze.cn,
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


def get_current_time_ms():
    return int(time.time() * 1000)


setup_examples_logger()

kwargs = json.loads(os.getenv("COZE_KWARGS") or "{}")


class AsyncWebsocketsChatEventHandlerSub(AsyncWebsocketsChatEventHandler):
    """
    Class is not required, you can also use Dict to set callback
    """

    logid = ""
    input_audio_buffer_completed_at = 0
    conversation_chat_created_at = 0
    conversation_audio_transcript_completed = 0
    text_first_token = 0
    audio_first_token = 0

    async def on_error(self, cli: AsyncWebsocketsChatClient, e: Exception):
        import traceback

        log_info(f"Error occurred: {str(e)}")
        log_info(f"Stack trace:\n{traceback.format_exc()}")

    async def on_conversation_chat_created(self, cli: AsyncWebsocketsChatClient, event: ConversationChatCreatedEvent):
        self.logid = event.detail.logid
        self.conversation_chat_created_at = get_current_time_ms()

    async def on_conversation_audio_transcript_completed(
        self, cli: AsyncWebsocketsChatClient, event: ConversationAudioTranscriptCompletedEvent
    ):
        self.conversation_audio_transcript_completed = get_current_time_ms()

    async def on_conversation_message_delta(self, cli: AsyncWebsocketsChatClient, event: ConversationMessageDeltaEvent):
        if self.text_first_token == 0:
            self.text_first_token = get_current_time_ms()

    async def on_conversation_audio_delta(self, cli: AsyncWebsocketsChatClient, event: ConversationAudioDeltaEvent):
        if self.audio_first_token == 0:
            self.audio_first_token = get_current_time_ms()


async def generate_audio(coze: AsyncCoze, text: str) -> List[bytes]:
    voices = await coze.audio.voices.list(**kwargs)
    content = await coze.audio.speech.create(
        input=text,
        voice_id=voices.items[0].voice_id,
        response_format=AudioFormat.WAV,
        sample_rate=24000,
        **kwargs,
    )
    return [data for data in content._raw_response.iter_bytes(chunk_size=1024)]


def cal_latency(latency_list: List[int]) -> str:
    if latency_list is None or len(latency_list) == 0:
        return "0"
    if len(latency_list) == 1:
        return f"{latency_list[0]}"
    res = latency_list.copy()
    res.sort()
    return "%2d" % ((sum(res[:-1]) * 1.0) / (len(res) - 1))


async def test_latency(coze: AsyncCoze, bot_id: str, audios: List[bytes]) -> AsyncWebsocketsChatEventHandlerSub:
    handler = AsyncWebsocketsChatEventHandlerSub()
    chat = coze.websockets.chat.create(
        bot_id=bot_id,
        on_event=handler,
        **kwargs,
    )

    # Create and connect WebSocket client
    async with chat() as client:
        # Read and send audio data
        for delta in audios:
            await client.input_audio_buffer_append(
                InputAudioBufferAppendEvent.Data.model_validate(
                    {
                        "delta": delta,
                    }
                )
            )
            # sleep(len(delta)*1.0/24000/2) # ms
        sleep(1.5)
        await client.input_audio_buffer_complete()
        handler.input_audio_buffer_completed_at = int(time.time() * 1000)
        await client.wait(
            events=[WebsocketsEventType.CONVERSATION_MESSAGE_DELTA, WebsocketsEventType.CONVERSATION_AUDIO_DELTA]
        )

    return handler


async def main():
    coze_api_token = get_coze_api_token()
    coze_api_base = get_coze_api_base()
    bot_id = os.getenv("COZE_BOT_ID")
    text = os.getenv("COZE_TEXT") or "讲个笑话"

    # Initialize Coze client
    coze = AsyncCoze(
        auth=TokenAuth(coze_api_token),
        base_url=coze_api_base,
    )
    # Initialize Audio
    audios = await generate_audio(coze, text)

    times = 50
    text_latency = []
    audio_latency = []
    asr_latency = []
    for i in range(times):
        handler = await test_latency(coze, bot_id, audios)
        asr_latency.append(handler.conversation_audio_transcript_completed - handler.input_audio_buffer_completed_at)
        text_latency.append(handler.text_first_token - handler.input_audio_buffer_completed_at)
        audio_latency.append(handler.audio_first_token - handler.input_audio_buffer_completed_at)
        print(
            f"[latency.ws] {i}, asr: {cal_latency(asr_latency)}, text: {cal_latency(text_latency)} ms, audio: {cal_latency(audio_latency)} ms, log: {handler.logid}"
        )


if __name__ == "__main__":
    asyncio.run(main())
