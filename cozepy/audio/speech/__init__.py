from typing import Optional

from cozepy.model import DynamicStrEnum, FileHTTPResponse
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


class AudioFormat(DynamicStrEnum):
    WAV = "wav"
    PCM = "pcm"
    OGG_OPUS = "ogg_opus"
    MP3 = "mp3"


class LanguageCode(DynamicStrEnum):
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

    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(
        self,
        *,
        input: str,
        voice_id: str,
        response_format: AudioFormat = AudioFormat.MP3,
        speed: float = 1,
        sample_rate: int = 24000,
        **kwargs,
    ) -> FileHTTPResponse:
        """
        语音合成

        将指定文本合成为音频文件。
        接口描述
        此 API 用于将指定文本内容合成为自然流畅的音频，同步返回合成的音频文件，适用于有声书合成、智能客服语音、音视频配音等场景。合成音频文件之前，可以先调用查看音色列表 API，查看所有可用音色。
        调用语音合成 API 会产生语音合成费用，具体费用详情请参考音视频费用。

        :param input: 必选，合成语音的文本，长度限制 1024 字节（UTF-8编码）。
        :param voice_id: 必选，音色id
        :param response_format: 音频编码格式，wav / pcm / ogg_opus / mp3，默认为 mp3
        :param speed: 语速，[0.2,3]，默认为1，通常保留一位小数即可
        :param sample_rate: 采样率，可选值 [8000,16000,22050,24000,32000,44100,48000]，默认 24000
        """
        url = f"{self._base_url}/v1/audio/speech"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "input": input,
            "voice_id": voice_id,
            "response_format": response_format,
            "speed": speed,
            "sample_rate": sample_rate,
        }
        return self._requester.request("post", url, False, cast=FileHTTPResponse, headers=headers, body=body)


class AsyncSpeechClient(object):
    """
    speech service client.
    """

    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def create(
        self,
        *,
        input: str,
        voice_id: str,
        response_format: AudioFormat = AudioFormat.MP3,
        speed: float = 1,
        sample_rate: int = 24000,
        **kwargs,
    ) -> FileHTTPResponse:
        """
        语音合成

        将指定文本合成为音频文件。
        接口描述
        此 API 用于将指定文本内容合成为自然流畅的音频，同步返回合成的音频文件，适用于有声书合成、智能客服语音、音视频配音等场景。合成音频文件之前，可以先调用查看音色列表 API，查看所有可用音色。
        调用语音合成 API 会产生语音合成费用，具体费用详情请参考音视频费用。

        :param input: 必选，合成语音的文本，长度限制 1024 字节（UTF-8编码）。
        :param voice_id: 必选，音色id
        :param response_format: 音频编码格式，wav / pcm / ogg_opus / mp3，默认为 mp3
        :param speed: 语速，[0.2,3]，默认为1，通常保留一位小数即可
        :param sample_rate: 采样率，可选值 [8000,16000,22050,24000,32000,44100,48000]，默认 24000
        """
        url = f"{self._base_url}/v1/audio/speech"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "input": input,
            "voice_id": voice_id,
            "response_format": response_format,
            "speed": speed,
            "sample_rate": sample_rate,
        }
        return await self._requester.arequest("post", url, False, cast=FileHTTPResponse, headers=headers, body=body)
