import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Coze, TokenAuth
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_update_voiceprint_feature(respx_mock) -> str:
    logid = random_hex(10)
    raw_response = httpx.Response(
        200,
        json={"data": {}},
        headers={logid_key(): logid},
    )
    respx_mock.put("/v1/audio/voiceprint_groups/group_id/features/feature_id").mock(raw_response)
    return logid


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncVoiceprintGroupsFeatures:
    def test_sync_update_without_file(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        mock_logid = mock_update_voiceprint_feature(respx_mock)

        resp = coze.audio.voiceprint_groups.features.update(
            group_id="group_id",
            feature_id="feature_id",
            name="name",
            file=None,
        )
        assert resp.response.logid == mock_logid


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncVoiceprintGroupsFeatures:
    async def test_async_update_without_file(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        mock_logid = mock_update_voiceprint_feature(respx_mock)

        resp = await coze.audio.voiceprint_groups.features.update(
            group_id="group_id",
            feature_id="feature_id",
            name="name",
            file=None,
        )
        assert resp.response.logid == mock_logid
