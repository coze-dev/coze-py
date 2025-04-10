"""
This example shows how to record audio input, chat with the bot, and play audio response.
"""

import base64
import logging
import os
import sys
import tempfile
import wave
from pathlib import Path
from typing import Optional

try:
    import scipy.io.wavfile
except ImportError:
    print("Please install scipy first: pip install scipy")
    sys.exit(1)

try:
    import pyaudio
except ImportError:
    print("Please install pyaudio first: pip install pyaudio")
    sys.exit(1)
try:
    import sounddevice as sd
except ImportError:
    print("Please install sounddevice first: pip install sounddevice")
    sys.exit(1)

from cozepy import (
    COZE_CN_BASE_URL,
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


def select_input_device() -> int:
    """Select an input device from available devices"""
    p = pyaudio.PyAudio()

    # List available input devices
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get("deviceCount")

    print("\nPlease select an input device:")
    input_devices = []
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get("maxInputChannels")) > 0:
            device_info = p.get_device_info_by_host_api_device_index(0, i)
            print(f"Device {len(input_devices)}: {device_info.get('name')}")
            input_devices.append(i)

    # Let user choose input device
    while True:
        try:
            choice = int(input("\nPlease select input device number (0-" + str(len(input_devices) - 1) + "): "))
            if 0 <= choice < len(input_devices):
                input_device_index = input_devices[choice]
                break
            else:
                print("Invalid choice, please try again")
        except ValueError:
            print("Invalid input, please enter a number")

    print(f"\nUsing input device: {p.get_device_info_by_host_api_device_index(0, input_device_index).get('name')}")
    p.terminate()
    return input_device_index


def create_conversation() -> str:
    """Create a conversation"""
    return coze.chat.create(bot_id=bot_id, user_id=user_id).conversation_id


def record_audio(input_device_index: int) -> str:
    """Record audio from microphone and save to file"""
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    p = pyaudio.PyAudio()

    print("Recording... Press Ctrl-C to stop.")

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=input_device_index,
        frames_per_buffer=CHUNK,
    )

    frames = []

    try:
        print("Press Enter to stop recording...")
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
    except KeyboardInterrupt:
        pass

    print("Recording stopped")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save recording
    _, audio_path = tempfile.mkstemp(suffix=".wav")
    wf = wave.open(audio_path, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()

    return audio_path


def chat_with_audio(audio_file_path: str, conversation_id: str):
    # Call the coze.chat.stream api and save pcm audio data to wav file.
    audio_file = coze.files.upload(file=Path(audio_file_path))

    pcm_datas = b""
    print("\033[32m| >\033[0m ", end="", flush=True)
    for event in coze.chat.stream(
        bot_id=bot_id,
        user_id=user_id,
        conversation_id=conversation_id,
        additional_messages=[
            Message.build_user_question_objects(
                [
                    MessageObjectString.build_audio(file_id=audio_file.id),
                ]
            ),
        ],
    ):
        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            print(event.message.content, end="", flush=True)
        elif event.event == ChatEventType.CONVERSATION_AUDIO_DELTA:
            pcm_datas += base64.b64decode(event.message.content)

    _, wav_audio_path = tempfile.mkstemp(suffix=".wav")
    write_pcm_to_wav_file(pcm_datas, wav_audio_path)

    return wav_audio_path


def play_audio(wav_audio_path: str):
    fs, data = scipy.io.wavfile.read(wav_audio_path)
    sd.play(data, fs)
    sd.wait()  # Wait until the audio finishes playing


if __name__ == "__main__":
    # Record and chat with audio
    print("Stop by pressing Ctrl-C ...")

    input_device_index = select_input_device()

    conversation_id = create_conversation()

    while True:
        audio_file_path = record_audio(input_device_index)
        wav_audio_path = chat_with_audio(audio_file_path, conversation_id)
        play_audio(wav_audio_path)
