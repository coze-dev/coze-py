from cozepy.request import Requester
from cozepy.util import http_base_url_to_ws, remove_url_trailing_slash

from .audio import AsyncWebsocketsAudioClient, WebsocketsAudioClient
from .chat import AsyncWebsocketsChatBuildClient, WebsocketsChatBuildClient


class WebsocketsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = http_base_url_to_ws(remove_url_trailing_slash(base_url))
        self._requester = requester

    @property
    def audio(self) -> WebsocketsAudioClient:
        return WebsocketsAudioClient(
            base_url=self._base_url,
            requester=self._requester,
        )

    @property
    def chat(self) -> WebsocketsChatBuildClient:
        return WebsocketsChatBuildClient(
            base_url=self._base_url,
            requester=self._requester,
        )


class AsyncWebsocketsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = http_base_url_to_ws(remove_url_trailing_slash(base_url))
        self._requester = requester

    @property
    def audio(self) -> AsyncWebsocketsAudioClient:
        return AsyncWebsocketsAudioClient(
            base_url=self._base_url,
            requester=self._requester,
        )

    @property
    def chat(self) -> AsyncWebsocketsChatBuildClient:
        return AsyncWebsocketsChatBuildClient(
            base_url=self._base_url,
            requester=self._requester,
        )
