import asyncio
import json
import logging
import os
import time
from typing import List, Optional

from cozepy import (
    COZE_CN_BASE_URL,
    AsyncCoze,
    AsyncTokenAuth,
    AsyncWebsocketsChatClient,
    AsyncWebsocketsChatEventHandler,
    AudioFormat,
    ConversationAudioDeltaEvent,
    ConversationAudioTranscriptCompletedEvent,
    ConversationChatCreatedEvent,
    ConversationMessageDeltaEvent,
    DeviceOAuthApp,
    InputAudioBufferAppendEvent,
    WebsocketsEventType,
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


def get_current_time_ms():
    return int(time.time() * 1000)


def green_text(s: str) -> str:
    return f"\033[32m{s}\033[0m"


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
    # content.write_to_file("test.wav")
    return [data for data in content._raw_response.iter_bytes(chunk_size=1024)]


def cal_latency(current: int, latency_list: List[int]) -> str:
    if latency_list is None or len(latency_list) == 0:
        return "No latency data"
    if len(latency_list) == 1:
        return f"P99={latency_list[0]}ms, P90={latency_list[0]}ms, AVG={latency_list[0]}ms"

    # 对延迟数据进行排序
    sorted_latency = sorted(latency_list)
    length = len(sorted_latency)

    def fix_index(index):
        if index < 0:
            return 0
        if index >= length:
            return length - 1
        return index

    # 计算 P99
    p99_index = fix_index(round(length * 0.99) - 1)
    p99 = sorted_latency[p99_index]

    # 计算 P90
    p90_index = fix_index(round(length * 0.90) - 1)
    p90 = sorted_latency[p90_index]

    # 计算平均值
    avg = sum(sorted_latency) / length

    return f"P99={p99}ms, P90={p90}ms, AVG={avg:.2f}ms, CURRENT={current}ms"


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
            await asyncio.sleep(len(delta) * 1.0 / 24000 / 2)

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
        auth=AsyncTokenAuth(coze_api_token),
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
        asr = handler.conversation_audio_transcript_completed - handler.input_audio_buffer_completed_at
        text = handler.text_first_token - handler.input_audio_buffer_completed_at
        audio = handler.audio_first_token - handler.input_audio_buffer_completed_at

        asr_latency.append(asr)
        text_latency.append(text)
        audio_latency.append(audio)
        print(
            f"[latency.ws] {i}, {green_text('asr')}: {cal_latency(asr, asr_latency)}, {green_text('text')}: {cal_latency(text, text_latency)}, {green_text('audio')}: {cal_latency(audio, audio_latency)}, {green_text('log')}: {handler.logid}"
        )


if __name__ == "__main__":
    # COZE_API_TOKEN=xx COZE_BOT_ID=xx COZE_TEXT=xx COZE_LOG=error python examples/benchmark_websockets_chat.py
    asyncio.run(main())
