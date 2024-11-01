from typing import Optional

from cozepy.auth import Auth
from cozepy.model import CozeModel
from cozepy.request import Requester


class CreateRoomResult(CozeModel):
    # Token to join the room
    token: str
    # The id of user
    uid: str
    # The id of room
    room_id: str
    # App id to join the room
    app_id: str


class RoomsClient(object):
    """
    Room service client.
    """

    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester

    def create(self, *, bot_id: str, voice_id: str) -> CreateRoomResult:
        """
        create rtc room

        :param bot_id: The id of the bot.
        :param voice_id: The voice id of the voice.
        :return:
        """
        url = f"{self._base_url}/v1/audio/rooms"
        body = {
            "bot_id": bot_id,
            "voice_id": voice_id,
        }
        return self._requester.request("post", url, stream=False, cast=CreateRoomResult, body=body)


class AsyncRoomsClient(object):
    """
    Room service async client.
    """

    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester

    async def create(self, *, bot_id: str, voice_id: Optional[str] = None) -> CreateRoomResult:
        """
        create rtc room

        :param bot_id: The id of the bot.
        :param voice_id: The voice id of the voice.
        :return:
        """
        url = f"{self._base_url}/v1/audio/rooms"
        body = {
            "bot_id": bot_id,
            "voice_id": voice_id,
        }
        return await self._requester.arequest("post", url, stream=False, cast=CreateRoomResult, body=body)
