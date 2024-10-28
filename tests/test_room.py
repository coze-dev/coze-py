import httpx
import pytest

from cozepy import AsyncCoze, Coze, TokenAuth
from cozepy import CreateRoomResult


@pytest.mark.respx(base_url="https://api.coze.com")
class TestRooms:
    def test_sync_rooms_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/audio/rooms").mock(
            httpx.Response(
                200,
                json={
                    "data": CreateRoomResult(
                        token="JOIN_ROOM_TOKEN", uid="UID", room_id="ROOM_ID", app_id="APP_ID"
                    ).model_dump()
                },
            )
        )

        res = coze.rooms.create(bot_id="BOT_ID", voice_id="VOICE_ID")
        assert res
        assert res.token == "JOIN_ROOM_TOKEN"
        assert res.room_id == room_id
        assert res.uid == uid
        assert res.app_id == app_id


class TestAsyncRooms:
    async def test_async_rooms_create(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/audio/rooms").mock(
            httpx.Response(
                200,
                json={
                    "data": CreateRoomResult(
                        token="JOIN_ROOM_TOKEN", uid="UID", room_id="ROOM_ID", app_id="APP_ID"
                    ).model_dump()
                },
            )
        )

        res = await coze.rooms.create(bot_id="BOT_ID", voice_id="VOICE_ID")
        assert res
        assert res.token == "JOIN_ROOM_TOKEN"
        assert res.room_id == "ROOM_ID"
        assert res.uid == "UID"
        assert res.app_id == "APP_ID"
