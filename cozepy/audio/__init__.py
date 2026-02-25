from typing import TYPE_CHECKING, Optional

from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash

if TYPE_CHECKING:
    from cozepy.audio.live import AsyncLiveClient, LiveClient
    from cozepy.audio.rooms import AsyncRoomsClient, RoomsClient
    from cozepy.audio.speech import AsyncSpeechClient, SpeechClient
    from cozepy.audio.transcriptions import AsyncTranscriptionsClient, TranscriptionsClient
    from cozepy.audio.voiceprint_groups import AsyncVoiceprintGroupsClient, VoiceprintGroupsClient
    from cozepy.audio.voices import AsyncVoicesClient, VoicesClient


class AudioClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._live: Optional[LiveClient] = None
        self._rooms: Optional[RoomsClient] = None
        self._speech: Optional[SpeechClient] = None
        self._transcriptions: Optional[TranscriptionsClient] = None
        self._voiceprint_groups: Optional[VoiceprintGroupsClient] = None
        self._voices: Optional[VoicesClient] = None

    @property
    def live(self) -> "LiveClient":
        if not self._live:
            from .live import LiveClient

            self._live = LiveClient(base_url=self._base_url, requester=self._requester)
        return self._live

    @property
    def rooms(self) -> "RoomsClient":
        if not self._rooms:
            from .rooms import RoomsClient

            self._rooms = RoomsClient(base_url=self._base_url, requester=self._requester)
        return self._rooms

    @property
    def speech(self) -> "SpeechClient":
        if not self._speech:
            from .speech import SpeechClient

            self._speech = SpeechClient(base_url=self._base_url, requester=self._requester)
        return self._speech

    @property
    def transcriptions(self) -> "TranscriptionsClient":
        if not self._transcriptions:
            from .transcriptions import TranscriptionsClient

            self._transcriptions = TranscriptionsClient(base_url=self._base_url, requester=self._requester)
        return self._transcriptions

    @property
    def voiceprint_groups(self) -> "VoiceprintGroupsClient":
        if not self._voiceprint_groups:
            from .voiceprint_groups import VoiceprintGroupsClient

            self._voiceprint_groups = VoiceprintGroupsClient(base_url=self._base_url, requester=self._requester)
        return self._voiceprint_groups

    @property
    def voices(self) -> "VoicesClient":
        if not self._voices:
            from .voices import VoicesClient

            self._voices = VoicesClient(base_url=self._base_url, requester=self._requester)
        return self._voices


class AsyncAudioClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._live: Optional[AsyncLiveClient] = None
        self._rooms: Optional[AsyncRoomsClient] = None
        self._speech: Optional[AsyncSpeechClient] = None
        self._transcriptions: Optional[AsyncTranscriptionsClient] = None
        self._voiceprint_groups: Optional[AsyncVoiceprintGroupsClient] = None
        self._voices: Optional[AsyncVoicesClient] = None

    @property
    def live(self) -> "AsyncLiveClient":
        if not self._live:
            from .live import AsyncLiveClient

            self._live = AsyncLiveClient(base_url=self._base_url, requester=self._requester)
        return self._live

    @property
    def rooms(self) -> "AsyncRoomsClient":
        if not self._rooms:
            from .rooms import AsyncRoomsClient

            self._rooms = AsyncRoomsClient(base_url=self._base_url, requester=self._requester)
        return self._rooms

    @property
    def speech(self) -> "AsyncSpeechClient":
        if not self._speech:
            from .speech import AsyncSpeechClient

            self._speech = AsyncSpeechClient(base_url=self._base_url, requester=self._requester)
        return self._speech

    @property
    def transcriptions(self) -> "AsyncTranscriptionsClient":
        if not self._transcriptions:
            from .transcriptions import AsyncTranscriptionsClient

            self._transcriptions = AsyncTranscriptionsClient(base_url=self._base_url, requester=self._requester)
        return self._transcriptions

    @property
    def voiceprint_groups(self) -> "AsyncVoiceprintGroupsClient":
        if not self._voiceprint_groups:
            from .voiceprint_groups import AsyncVoiceprintGroupsClient

            self._voiceprint_groups = AsyncVoiceprintGroupsClient(base_url=self._base_url, requester=self._requester)
        return self._voiceprint_groups

    @property
    def voices(self) -> "AsyncVoicesClient":
        if not self._voices:
            from .voices import AsyncVoicesClient

            self._voices = AsyncVoicesClient(base_url=self._base_url, requester=self._requester)
        return self._voices
