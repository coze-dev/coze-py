import httpx
import pytest

from cozepy import AsyncCoze, Coze, CreateRoomResult, TokenAuth
from cozepy.util import random_hex


@pytest.mark.respx(base_url="https://api.coze.com")
class TestRooms:
    def test_sync_rooms_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        room_id = random_hex(10)
        room_token = random_hex(10)
        app_id = random_hex(10)
        uid = random_hex(10)
        bot_id = random_hex(10)
        voice_id = random_hex(10)
        respx_mock.post("/v1/audio/rooms").mock(
            httpx.Response(
                200,
                json={"data": CreateRoomResult(token=room_token, uid=uid, room_id=room_id, app_id=app_id).model_dump()},
            )
        )

        res = coze.rooms.create(bot_id=bot_id, voice_id=voice_id)
        assert res
        assert res.token == room_token
        assert res.room_id == room_id
        assert res.uid == uid
        assert res.app_id == app_id


class TestAsyncRooms:
    async def test_async_rooms_create(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))
        room_id = random_hex(10)
        room_token = random_hex(10)
        app_id = random_hex(10)
        uid = random_hex(10)
        bot_id = random_hex(10)
        voice_id = random_hex(10)
        respx_mock.post("/v1/audio/rooms").mock(
            httpx.Response(
                200,
                json={"data": CreateRoomResult(token=room_token, uid=uid, room_id=room_id, app_id=app_id).model_dump()},
            )
        )

        res = await coze.rooms.create(bot_id=bot_id, voice_id=voice_id)
        assert res
        assert res.token == room_token
        assert res.room_id == room_id
        assert res.uid == uid
        assert res.app_id == app_id
