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
        create transcriptions

        :param file: The file to be translated.
        :return: create transcriptions result
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
        create transcriptions

        :param file: The file to be translated.
        :return: create transcriptions result
        """
        url = f"{self._base_url}/v1/audio/transcriptions"
        files = {"file": _try_fix_file(file)}
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest(
            "post", url, stream=False, cast=CreateTranscriptionsResp, headers=headers, files=files
        )
