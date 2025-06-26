import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Coze, LiveInfo, LiveType, StreamInfo, TokenAuth
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_live_info():
    return LiveInfo(
        app_id=random_hex(10),
        stream_infos=[
            StreamInfo(stream_id=random_hex(10), name=random_hex(10), live_type=LiveType.ORIGIN),
            StreamInfo(stream_id=random_hex(10), name=random_hex(10), live_type=LiveType.TRANSLATION),
        ],
    )


def mock_retrieve_live(respx_mock, live_id):
    live_info = mock_live_info()
    respx_mock.get(f"/v1/audio/live/{live_id}").mock(
        httpx.Response(
            200,
            json={"data": live_info.model_dump()},
            headers={logid_key(): random_hex(10)},
        )
    )
    return live_info


@pytest.mark.respx(base_url="https://api.coze.com")
class TestAudioLive:
    def test_sync_live_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        live_id = random_hex(10)
        mock_info = mock_retrieve_live(respx_mock, live_id)
        res = coze.audio.live.retrieve(live_id=live_id)
        assert res
        assert res.app_id == mock_info.app_id
        assert len(res.stream_infos) == len(mock_info.stream_infos)
        for r, m in zip(res.stream_infos, mock_info.stream_infos):
            assert r.stream_id == m.stream_id
            assert r.name == m.name
            assert r.live_type == m.live_type


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncAudioLive:
    async def test_async_live_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        live_id = random_hex(10)
        mock_info = mock_retrieve_live(respx_mock, live_id)
        res = await coze.audio.live.retrieve(live_id=live_id)
        assert res
        assert res.app_id == mock_info.app_id
        assert len(res.stream_infos) == len(mock_info.stream_infos)
        for r, m in zip(res.stream_infos, mock_info.stream_infos):
            assert r.stream_id == m.stream_id
            assert r.name == m.name
            assert r.live_type == m.live_type
