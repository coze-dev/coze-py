import asyncio
import json
import os

from cozepy import (
    AsyncCoze,
    AsyncWebsocketsChatClient,
    AsyncWebsocketsChatEventHandler,
    AudioFormat,
    ConversationAudioDeltaEvent,
    ConversationChatCompletedEvent,
    ConversationChatCreatedEvent,
    ConversationChatRequiresActionEvent,
    ConversationChatSubmitToolOutputsEvent,
    ConversationMessageDeltaEvent,
    InputAudioBufferAppendEvent,
    TokenAuth,
    ToolOutput,
)
from cozepy.log import log_info
from cozepy.util import write_pcm_to_wav_file
from examples.utils import get_coze_api_base, get_coze_api_token, setup_examples_logger

setup_examples_logger()

kwargs = json.loads(os.getenv("COZE_KWARGS") or "{}")


class AsyncWebsocketsChatEventHandlerSub(AsyncWebsocketsChatEventHandler):
    """
    Class is not required, you can also use Dict to set callback
    """

    delta = []

    async def on_error(self, cli: AsyncWebsocketsChatClient, e: Exception):
        import traceback

        log_info(f"Error occurred: {str(e)}")
        log_info(f"Stack trace:\n{traceback.format_exc()}")

    async def on_conversation_chat_created(self, cli: AsyncWebsocketsChatClient, event: ConversationChatCreatedEvent):
        log_info("[examples] asr completed, logid=%s", event.detail.logid)

    async def on_conversation_message_delta(self, cli: AsyncWebsocketsChatClient, event: ConversationMessageDeltaEvent):
        print("Received:", event.data.content)

    async def on_conversation_chat_requires_action(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationChatRequiresActionEvent
    ):
        def fake_run_local_plugin():
            # this is just fake outputs
            return event.data.required_action.submit_tool_outputs.tool_calls[0].function.arguments

        fake_output = fake_run_local_plugin()
        await cli.conversation_chat_submit_tool_outputs(
            ConversationChatSubmitToolOutputsEvent.Data.model_validate(
                {
                    "chat_id": event.data.id,
                    "tool_outputs": [
                        ToolOutput.model_validate(
                            {
                                "tool_call_id": event.data.required_action.submit_tool_outputs.tool_calls[0].id,
                                "output": fake_output,
                            }
                        )
                    ],
                }
            )
        )

    async def on_conversation_audio_delta(self, cli: AsyncWebsocketsChatClient, event: ConversationAudioDeltaEvent):
        self.delta.append(event.data.get_audio())

    async def on_conversation_chat_completed(
        self, cli: "AsyncWebsocketsChatClient", event: ConversationChatCompletedEvent
    ):
        log_info("[examples] Saving audio data to output.wav")
        write_pcm_to_wav_file(b"".join(self.delta), "output.wav")


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
    bot_id = os.getenv("COZE_BOT_ID")
    text = os.getenv("COZE_TEXT") or "你今天好吗? 今天天气不错呀"

    # Initialize Coze client
    coze = AsyncCoze(
        auth=TokenAuth(coze_api_token),
        base_url=coze_api_base,
    )
    # Initialize Audio
    speech_stream = wrap_coze_speech_to_iterator(coze, text)

    chat = coze.websockets.chat.create(
        bot_id=bot_id,
        on_event=AsyncWebsocketsChatEventHandlerSub(),
        **kwargs,
    )

    # Create and connect WebSocket client
    async with chat() as client:
        # Read and send audio data
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
