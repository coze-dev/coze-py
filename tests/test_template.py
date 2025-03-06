import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Coze, TemplateDuplicateResp, TokenAuth
from cozepy.util import random_hex


def mock_template_duplicate(respx_mock, entity_id, entity_type):
    respx_mock.post("/v1/templates/template_id/duplicate").mock(
        httpx.Response(
            200,
            json={
                "data": TemplateDuplicateResp(
                    entity_id=entity_id,
                    entity_type=entity_type,
                ).model_dump()
            },
        )
    )


@pytest.mark.respx(base_url="https://api.coze.com")
class TestTemplate:
    def test_sync_template_duplicate(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        entity_id = random_hex(10)
        entity_type = "agent"

        mock_template_duplicate(respx_mock, entity_id, entity_type)

        res = coze.templates.duplicate(template_id="template_id", workspace_id="workspace_id", name="name")
        assert res
        assert res.entity_id == entity_id
        assert res.entity_type == entity_type


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncTemplate:
    async def test_async_template_duplicate(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        entity_id = random_hex(10)
        entity_type = "agent"

        mock_template_duplicate(respx_mock, entity_id, entity_type)

        res = await coze.templates.duplicate(template_id="template_id", workspace_id="workspace_id", name="name")
        assert res
        assert res.entity_id == entity_id
        assert res.entity_type == entity_type
