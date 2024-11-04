from typing import TYPE_CHECKING, Optional

from cozepy.auth import Auth
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash

if TYPE_CHECKING:
    from .rooms import AsyncRoomsClient, RoomsClient
    from .speech import AsyncSpeechClient, SpeechClient
    from .voices import AsyncVoicesClient, VoicesClient


class AudioClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._auth = auth
        self._requester = requester

        self._rooms: Optional[RoomsClient] = None
        self._voices: Optional[VoicesClient] = None
        self._speech: Optional[SpeechClient] = None

    @property
    def rooms(self) -> "RoomsClient":
        if self._rooms is None:
            from .rooms import RoomsClient

            self._rooms = RoomsClient(base_url=self._base_url, auth=self._auth, requester=self._requester)
        return self._rooms

    @property
    def speech(self) -> "SpeechClient":
        if self._speech is None:
            from .speech import SpeechClient

            self._speech = SpeechClient(base_url=self._base_url, auth=self._auth, requester=self._requester)
        return self._speech

    @property
    def voices(self) -> "VoicesClient":
        if self._voices is None:
            from .voices import VoicesClient

            self._voices = VoicesClient(base_url=self._base_url, auth=self._auth, requester=self._requester)
        return self._voices


class AsyncAudioClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._auth = auth
        self._requester = requester

        self._rooms: Optional[AsyncRoomsClient] = None
        self._voices: Optional[AsyncVoicesClient] = None
        self._speech: Optional[AsyncSpeechClient] = None

    @property
    def rooms(self) -> "AsyncRoomsClient":
        if self._rooms is None:
            from .rooms import AsyncRoomsClient

            self._rooms = AsyncRoomsClient(base_url=self._base_url, auth=self._auth, requester=self._requester)
        return self._rooms

    @property
    def speech(self) -> "AsyncSpeechClient":
        if self._speech is None:
            from .speech import AsyncSpeechClient

            self._speech = AsyncSpeechClient(base_url=self._base_url, auth=self._auth, requester=self._requester)
        return self._speech

    @property
    def voices(self) -> "AsyncVoicesClient":
        if self._voices is None:
            from .voices import AsyncVoicesClient

            self._voices = AsyncVoicesClient(base_url=self._base_url, auth=self._auth, requester=self._requester)
        return self._voices
