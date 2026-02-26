from enum import Enum
from typing import List, Optional

from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


class LiveType(str, Enum):
    ORIGIN = "origin"
    TRANSLATION = "translation"


class StreamInfo(CozeModel):
    stream_id: str
    name: str
    live_type: LiveType


class LiveInfo(CozeModel):
    app_id: str
    stream_infos: List[StreamInfo]


class LiveClient(object):
    """
    Live service client.
    """

    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def retrieve(
        self,
        *,
        live_id: str,
        **kwargs,
    ) -> LiveInfo:
        """
        retrieve live

        :param live_id: The id of the live.
        :return: live info
        """
        url = f"{self._base_url}/v1/audio/live/{live_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("get", url, False, cast=LiveInfo, headers=headers)


class AsyncLiveClient(object):
    """
    Room service async client.
    """

    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def retrieve(
        self,
        *,
        live_id: str,
        **kwargs,
    ) -> LiveInfo:
        """
        retrieve live

        :param live_id: The id of the live.
        :return: live info
        """
        url = f"{self._base_url}/v1/audio/live/{live_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest("get", url, False, cast=LiveInfo, headers=headers)
