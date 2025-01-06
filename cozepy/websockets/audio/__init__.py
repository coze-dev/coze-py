from cozepy.auth import Auth
from cozepy.request import Requester

from .speech import AsyncWebsocketsAudioSpeechClient
from .transcriptions import AsyncWebsocketsAudioTranscriptionsClient


class AsyncWebsocketsAudioClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester

    @property
    def transcriptions(self) -> "AsyncWebsocketsAudioTranscriptionsClient":
        return AsyncWebsocketsAudioTranscriptionsClient(
            base_url=self._base_url,
            auth=self._auth,
            requester=self._requester,
        )

    @property
    def speech(self) -> "AsyncWebsocketsAudioSpeechClient":
        return AsyncWebsocketsAudioSpeechClient(
            base_url=self._base_url,
            auth=self._auth,
            requester=self._requester,
        )
