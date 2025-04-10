"""
This example is about how to use audio api.
"""

import logging
import os

from cozepy import (
    COZE_CN_BASE_URL,
    Coze,
    TokenAuth,
    setup_logging,
)

# Get an access_token through personal access token or oauth.
coze_api_token = os.getenv("COZE_API_TOKEN")
# The default access is api.coze.cn, but if you need to access api.coze.com,
# please use base_url to configure the api endpoint to access
coze_api_base = os.getenv("COZE_API_BASE") or COZE_CN_BASE_URL
# Whether to print detailed logs
is_debug = os.getenv("DEBUG")

if is_debug:
    setup_logging(logging.DEBUG)

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)


def get_voice_id() -> str:
    if os.getenv("COZE_VOICE_ID"):
        return os.getenv("COZE_VOICE_ID")
    voices = coze.audio.voices.list()
    for voice in voices.items:
        print("Get voice:", voice.voice_id, voice.name)

    return voices.items[-1].voice_id


input_text = os.getenv("COZE_SPEECH_INPUT") or "你好世界"
voice_id = get_voice_id()

speech_file = coze.audio.speech.create(input=input_text, voice_id=voice_id)
file_path = os.path.join(os.path.expanduser("~"), "Downloads", f"coze_{voice_id}_example.mp3")
speech_file.write_to_file(file_path)
print(f"Create speech of voice: {voice_id} to file: {file_path}")
