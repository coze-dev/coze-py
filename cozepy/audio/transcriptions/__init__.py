from typing import Optional

from cozepy.files import FileTypes, _try_fix_file
from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


class CreateTranscriptionsResp(CozeModel):
    # The text of translation
    text: str


class TranscriptionsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(
        self,
        *,
        file: FileTypes,
        **kwargs,
    ) -> CreateTranscriptionsResp:
        """
        语音识别
        限制说明
        每个音频文件最大为 10 MB，并且时长需小于 30 分钟。
        将音频文件转录为文本。
        接口描述
        此 API 用于将指定音频文件转录为文本。
        语音文件的具体限制如下： 文件格式 支持的文件格式包括 ogg、mp3 和 wav。
        文件大小 上传的音频文件的采样率和码率等参数无限制。
        如果语音文件过大，建议调用 WebSocket 的 双向流式语音识别 API 分片上传文件。
        调用语音识别 API 会产生 语音识别费用 ，具体费用详情请参考 音视频费用 。
        """
        url = f"{self._base_url}/v1/audio/transcriptions"
        headers: Optional[dict] = kwargs.get("headers")
        files = {"file": _try_fix_file(file)}
        return self._requester.request(
            "post", url, stream=False, cast=CreateTranscriptionsResp, headers=headers, files=files
        )


class AsyncTranscriptionsClient(object):
    """
    Room service async client.
    """

    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def create(
        self,
        *,
        file: FileTypes,
        **kwargs,
    ) -> CreateTranscriptionsResp:
        """
        语音识别
        支持的文件格式包括 ogg、mp3 和 wav。
        每个音频文件最大为 10 MB，并且时长需小于 30 分钟。
        上传的音频文件的采样率和码率等参数无限制。
        如果语音文件过大，建议调用 WebSocket 的 双向流式语音识别 API 分片上传文件。
        限制说明
        文件大小 将音频文件转录为文本。
        接口描述
        此 API 用于将指定音频文件转录为文本。
        语音文件的具体限制如下： 调用语音识别 API 会产生 语音识别费用 ，具体费用详情请参考 音视频费用 。
        文件格式
        """
        url = f"{self._base_url}/v1/audio/transcriptions"
        headers: Optional[dict] = kwargs.get("headers")
        files = {"file": _try_fix_file(file)}
        return await self._requester.arequest(
            "post", url, stream=False, cast=CreateTranscriptionsResp, headers=headers, files=files
        )
