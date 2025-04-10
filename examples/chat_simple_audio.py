"""
This example is about how to chat with audio input and handle audio response.
"""

import base64
import logging
import os
import random
import sys
from pathlib import Path
from typing import Optional

from cozepy import (
    COZE_CN_BASE_URL,
    AudioFormat,
    ChatEventType,
    Coze,
    DeviceOAuthApp,
    Message,
    MessageObjectString,
    TokenAuth,
    setup_logging,
)
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


# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=get_coze_api_token()), base_url=get_coze_api_base())
# Create a bot instance in Coze, copy the last number from the web link as the bot's ID.
bot_id = os.getenv("COZE_BOT_ID")
# The user id identifies the identity of a user. Developers can use a custom business ID
# or a random string.
user_id = "user id"
# Whether to print detailed logs
is_debug = os.getenv("DEBUG")

if is_debug:
    setup_logging(logging.DEBUG)


# Get and upload audio file
def get_audio_filepath() -> str:
    if len(sys.argv) > 1:
        # Get it from the program running parameters:
        # python examples/chat_audio.py ~/Downloads/input.wav
        print(f"Get audio filepath from arg: {sys.argv[1]}")
        return sys.argv[1]

    voices = [i for i in coze.audio.voices.list()]
    voice = random.choice(voices)
    print(f"Get random voice: {voice.voice_id} {voice.name} from voices list of length: {len(voices)}")

    input_text = "你是基于什么大模型构建的"
    audio_path = os.path.join(os.path.expanduser("~"), "Downloads", f"coze_{voice.voice_id}_{input_text}.wav")

    audio = coze.audio.speech.create(input=input_text, voice_id=voice.voice_id, response_format=AudioFormat.WAV)

    audio.write_to_file(audio_path)

    print(f"Get audio filepath from speech api: {audio_path}")
    return audio_path


audio_file_path = get_audio_filepath()
audio_file = coze.files.upload(file=Path(audio_file_path))


# Call the coze.chat.stream api and save pcm audio data to wav file.
pcm_datas = b""
for event in coze.chat.stream(
    bot_id=bot_id,
    user_id=user_id,
    additional_messages=[
        Message.build_user_question_objects(
            [
                MessageObjectString.build_audio(file_id=audio_file.id),
            ]
        ),
    ],
):
    if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
        message = event.message
        print(event.message.content, end="", flush=True)
    elif event.event == ChatEventType.CONVERSATION_AUDIO_DELTA:
        pcm_datas += base64.b64decode(event.message.content)

wav_audio_path = os.path.join(os.path.expanduser("~"), "Downloads", "coze_response_audio.wav")
write_pcm_to_wav_file(pcm_datas, wav_audio_path)
print(f"\nGet audio response from chat stream, save to {wav_audio_path}")
