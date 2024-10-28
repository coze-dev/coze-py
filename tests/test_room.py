import httpx
import pytest

from cozepy import AsyncCoze, Coze, CreateRoomResult, TokenAuth
from cozepy.util import random_hex


def mock_create_room(respx_mock):
    res = CreateRoomResult(token=random_hex(10), uid=random_hex(10), room_id=random_hex(10), app_id=random_hex(10))

    respx_mock.post("/v1/audio/rooms").mock(
        httpx.Response(
            200,
            json={"data": res.model_dump()},
        )
    )

    return res


@pytest.mark.respx(base_url="https://api.coze.com")
class TestRooms:
    def test_sync_rooms_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        bot_id = random_hex(10)
        voice_id = random_hex(10)
        mock_res = mock_create_room(respx_mock)

        res = coze.rooms.create(bot_id=bot_id, voice_id=voice_id)
        assert res
        assert res.token == mock_res.token
        assert res.room_id == mock_res.room_id
        assert res.uid == mock_res.uid
        assert res.app_id == mock_res.app_id


class TestAsyncRooms:
    async def test_async_rooms_create(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        bot_id = random_hex(10)
        voice_id = random_hex(10)
        mock_res = mock_create_room(respx_mock)

        res = await coze.rooms.create(bot_id=bot_id, voice_id=voice_id)
        assert res
        assert res.token == mock_res.token
        assert res.room_id == mock_res.room_id
        assert res.uid == mock_res.uid
        assert res.app_id == mock_res.app_id
