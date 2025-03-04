from cozepy.request import Requester

from .speech import AsyncWebsocketsAudioSpeechBuildClient, WebsocketsAudioSpeechBuildClient
from .transcriptions import AsyncWebsocketsAudioTranscriptionsBuildClient, WebsocketsAudioTranscriptionsBuildClient


class WebsocketsAudioClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = base_url
        self._requester = requester

    @property
    def transcriptions(self) -> "WebsocketsAudioTranscriptionsBuildClient":
        return WebsocketsAudioTranscriptionsBuildClient(
            base_url=self._base_url,
            requester=self._requester,
        )

    @property
    def speech(self) -> "WebsocketsAudioSpeechBuildClient":
        return WebsocketsAudioSpeechBuildClient(
            base_url=self._base_url,
            requester=self._requester,
        )


class AsyncWebsocketsAudioClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = base_url
        self._requester = requester

    @property
    def transcriptions(self) -> "AsyncWebsocketsAudioTranscriptionsBuildClient":
        return AsyncWebsocketsAudioTranscriptionsBuildClient(
            base_url=self._base_url,
            requester=self._requester,
        )

    @property
    def speech(self) -> "AsyncWebsocketsAudioSpeechBuildClient":
        return AsyncWebsocketsAudioSpeechBuildClient(
            base_url=self._base_url,
            requester=self._requester,
        )
