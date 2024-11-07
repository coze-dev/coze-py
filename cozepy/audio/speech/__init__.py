from enum import Enum

from cozepy.auth import Auth
from cozepy.model import FileHTTPResponse
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


class AudioFormat(str, Enum):
    WAV = "wav"
    PCM = "pcm"
    OGG_OPUS = "ogg_opus"
    MP3 = "mp3"


class LanguageCode(str, Enum):
    ZH = "zh"
    EN = "en"
    JA = "ja"
    ES = "es"
    ID = "id"
    PT = "pt"


class SpeechClient(object):
    """
    speech service client.
    """

    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._auth = auth
        self._requester = requester

    def create(
        self, *, input: str, voice_id: str, response_format: AudioFormat = AudioFormat.MP3, speed: float = 1
    ) -> FileHTTPResponse:
        """
        Generate speech audio from input text with specified voice

        :param input: The text to generate audio for. Maximum length is 1024 characters.
        :param voice_id: The voice ID to generate audio with, obtained via .audio.voices.list
        :param response_format: Audio encoding format, wav / pcm / ogg_opus / mp3, defaults to mp3
        :param speed: Speech speed, [0.2,3], defaults to 1, typically one decimal place is sufficient
        :return: The synthesized audio file content
        """
        url = f"{self._base_url}/v1/audio/speech"
        body = {
            "input": input,
            "voice_id": voice_id,
            "response_format": response_format,
            "speed": speed,
        }
        return self._requester.request("post", url, stream=False, cast=FileHTTPResponse, body=body)


class AsyncSpeechClient(object):
    """
    speech service client.
    """

    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._auth = auth
        self._requester = requester

    async def create(
        self, *, input: str, voice_id: str, response_format: AudioFormat = AudioFormat.MP3, speed: float = 1
    ) -> FileHTTPResponse:
        """
        Generate speech audio from input text with specified voice

        :param input: The text to generate audio for. Maximum length is 1024 characters.
        :param voice_id: The voice ID to generate audio with, obtained via .audio.voices.list
        :param response_format: Audio encoding format, wav / pcm / ogg_opus / mp3, defaults to mp3
        :param speed: Speech speed, [0.2,3], defaults to 1, typically one decimal place is sufficient
        :return: The synthesized audio file content
        """
        url = f"{self._base_url}/v1/audio/speech"
        body = {
            "input": input,
            "voice_id": voice_id,
            "response_format": response_format,
            "speed": speed,
        }
        return await self._requester.arequest("post", url, stream=False, cast=FileHTTPResponse, body=body)
