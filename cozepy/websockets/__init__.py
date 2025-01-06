from cozepy import Auth
from cozepy.request import Requester
from cozepy.util import http_base_url_to_ws, remove_url_trailing_slash

from .audio import AsyncWebsocketsAudioClient
from .chat import AsyncWebsocketsChatClient


class AsyncWebsocketsClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = http_base_url_to_ws(remove_url_trailing_slash(base_url))
        self._auth = auth
        self._requester = requester

    @property
    def audio(self) -> AsyncWebsocketsAudioClient:
        return AsyncWebsocketsAudioClient(
            base_url=self._base_url,
            auth=self._auth,
            requester=self._requester,
        )

    @property
    def chat(self) -> AsyncWebsocketsChatClient:
        return AsyncWebsocketsChatClient(
            base_url=self._base_url,
            auth=self._auth,
            requester=self._requester,
        )
