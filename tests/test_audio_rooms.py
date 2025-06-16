import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Coze, CreateRoomResp, TokenAuth
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_create_room(respx_mock):
    create_room_res = CreateRoomResp(
        token=random_hex(10),
        uid=random_hex(10),
        room_id=random_hex(10),
        app_id=random_hex(10),
    )
    create_room_res._raw_response = httpx.Response(
        200,
        json={"data": create_room_res.model_dump()},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.post("/v1/audio/rooms").mock(create_room_res._raw_response)

    return create_room_res


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncAudioRooms:
    def test_sync_rooms_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        bot_id = random_hex(10)
        voice_id = random_hex(10)
        mock_res = mock_create_room(respx_mock)

        res = coze.audio.rooms.create(bot_id=bot_id, voice_id=voice_id)
        assert res
        assert res.response.logid == mock_res.response.logid
        assert res.token == mock_res.token
        assert res.room_id == mock_res.room_id
        assert res.uid == mock_res.uid
        assert res.app_id == mock_res.app_id


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncAudioRooms:
    async def test_async_rooms_create(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        bot_id = random_hex(10)
        voice_id = random_hex(10)
        mock_res = mock_create_room(respx_mock)

        res = await coze.audio.rooms.create(bot_id=bot_id, voice_id=voice_id)
        assert res
        assert res.response.logid is not None
        assert res.response.logid == mock_res.response.logid
        assert res.token == mock_res.token
        assert res.room_id == mock_res.room_id
        assert res.uid == mock_res.uid
        assert res.app_id == mock_res.app_id
