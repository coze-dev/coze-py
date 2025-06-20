from typing import TYPE_CHECKING, Optional

from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash

if TYPE_CHECKING:
    from .live import AsyncLiveClient, LiveClient
    from .rooms import AsyncRoomsClient, RoomsClient
    from .speech import AsyncSpeechClient, SpeechClient
    from .transcriptions import AsyncTranscriptionsClient, TranscriptionsClient
    from .voiceprint_groups import AsyncVoiceprintGroupsClient, VoiceprintGroupsClient
    from .voices import AsyncVoicesClient, VoicesClient


class AudioClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

        self._rooms: Optional[RoomsClient] = None
        self._voices: Optional[VoicesClient] = None
        self._speech: Optional[SpeechClient] = None
        self._transcriptions: Optional[TranscriptionsClient] = None
        self._voiceprint_groups: Optional[VoiceprintGroupsClient] = None
        self._live: Optional[LiveClient] = None

    @property
    def rooms(self) -> "RoomsClient":
        if self._rooms is None:
            from .rooms import RoomsClient

            self._rooms = RoomsClient(base_url=self._base_url, requester=self._requester)
        return self._rooms

    @property
    def speech(self) -> "SpeechClient":
        if self._speech is None:
            from .speech import SpeechClient

            self._speech = SpeechClient(base_url=self._base_url, requester=self._requester)
        return self._speech

    @property
    def transcriptions(self) -> "TranscriptionsClient":
        if self._transcriptions is None:
            from .transcriptions import TranscriptionsClient

            self._transcriptions = TranscriptionsClient(base_url=self._base_url, requester=self._requester)
        return self._transcriptions

    @property
    def voices(self) -> "VoicesClient":
        if self._voices is None:
            from .voices import VoicesClient

            self._voices = VoicesClient(base_url=self._base_url, requester=self._requester)
        return self._voices

    @property
    def voiceprint_groups(self) -> "VoiceprintGroupsClient":
        if self._voiceprint_groups is None:
            from .voiceprint_groups import VoiceprintGroupsClient

            self._voiceprint_groups = VoiceprintGroupsClient(base_url=self._base_url, requester=self._requester)
        return self._voiceprint_groups

    @property
    def live(self) -> "LiveClient":
        if self._live is None:
            from .live import LiveClient

            self._live = LiveClient(base_url=self._base_url, requester=self._requester)
        return self._live


class AsyncAudioClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

        self._rooms: Optional[AsyncRoomsClient] = None
        self._voices: Optional[AsyncVoicesClient] = None
        self._speech: Optional[AsyncSpeechClient] = None
        self._transcriptions: Optional[AsyncTranscriptionsClient] = None
        self._voiceprint_groups: Optional[AsyncVoiceprintGroupsClient] = None
        self._live: Optional[AsyncLiveClient] = None

    @property
    def rooms(self) -> "AsyncRoomsClient":
        if self._rooms is None:
            from .rooms import AsyncRoomsClient

            self._rooms = AsyncRoomsClient(base_url=self._base_url, requester=self._requester)
        return self._rooms

    @property
    def speech(self) -> "AsyncSpeechClient":
        if self._speech is None:
            from .speech import AsyncSpeechClient

            self._speech = AsyncSpeechClient(base_url=self._base_url, requester=self._requester)
        return self._speech

    @property
    def voices(self) -> "AsyncVoicesClient":
        if self._voices is None:
            from .voices import AsyncVoicesClient

            self._voices = AsyncVoicesClient(base_url=self._base_url, requester=self._requester)
        return self._voices

    @property
    def transcriptions(self) -> "AsyncTranscriptionsClient":
        if self._transcriptions is None:
            from .transcriptions import AsyncTranscriptionsClient

            self._transcriptions = AsyncTranscriptionsClient(base_url=self._base_url, requester=self._requester)
        return self._transcriptions

    @property
    def voiceprint_groups(self) -> "AsyncVoiceprintGroupsClient":
        if self._voiceprint_groups is None:
            from .voiceprint_groups import AsyncVoiceprintGroupsClient

            self._voiceprint_groups = AsyncVoiceprintGroupsClient(base_url=self._base_url, requester=self._requester)
        return self._voiceprint_groups

    @property
    def live(self) -> "AsyncLiveClient":
        if self._live is None:
            from .live import AsyncLiveClient

            self._live = AsyncLiveClient(base_url=self._base_url, requester=self._requester)
        return self._live
