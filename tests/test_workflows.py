import httpx
import pytest

from cozepy import (
    AsyncCoze,
    AsyncTokenAuth,
    Coze,
    TokenAuth,
    WorkflowBasic,
    WorkflowUserInfo,
    WorkflowVersionInfo,
)
from cozepy.util import random_hex
from cozepy.workflows import WorkflowInfo
from tests.test_util import logid_key


def mock_workflow_basic(workflow_id: str) -> WorkflowBasic:
    return WorkflowBasic(
        workflow_id=workflow_id,
        workflow_name="name",
        description="description",
        icon_url="icon_url",
        app_id="app_id",
        created_at=1699574400,
        updated_at=1699574400,
        creator=None,
    )


def mock_workflow_info(workflow_id: str) -> WorkflowInfo:
    return WorkflowInfo(
        workflow_detail=mock_workflow_basic(workflow_id),
    )


def mock_workflow_version(workflow_id: str) -> WorkflowVersionInfo:
    return WorkflowVersionInfo(
        version="1.0.0",
        description="Initial version",
        created_at="1699488000",
        updated_at="1699488000",
        workflow_id=workflow_id,
        creator=WorkflowUserInfo(id="user_id", name="User Name"),
    )


def mock_workflow_list(respx_mock):
    res = {
        "items": [
            mock_workflow_basic("w1").model_dump(),
            mock_workflow_basic("w2").model_dump(),
        ],
        "has_more": False,
    }
    raw_response = httpx.Response(200, json={"data": res}, headers={logid_key(): random_hex(10)})
    respx_mock.get(
        "/v1/workflows",
    ).mock(raw_response)
    return res


def mock_workflow_retrieve(respx_mock, workflow_id: str):
    res = mock_workflow_info(workflow_id)
    res._raw_response = httpx.Response(200, json={"data": res.model_dump()}, headers={logid_key(): random_hex(10)})
    respx_mock.get(
        f"/v1/workflows/{workflow_id}",
    ).mock(res._raw_response)
    return res


def mock_workflow_version_list(respx_mock, workflow_id: str):
    res = {
        "items": [
            mock_workflow_version(workflow_id).model_dump(),
            mock_workflow_version(workflow_id).model_dump(),
        ],
        "has_more": False,
    }
    raw_response = httpx.Response(200, json={"data": res}, headers={logid_key(): random_hex(10)})
    respx_mock.get(
        f"/v1/workflows/{workflow_id}/versions",
    ).mock(raw_response)
    return res


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncWorkflows:
    def test_sync_workflows_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        mock_workflow_list(respx_mock)
        paged = coze.workflows.list(page_num=1, page_size=2)
        items = list(paged)
        assert len(items) == 2
        assert items[0].workflow_id == "w1"
        assert items[1].workflow_id == "w2"

    def test_sync_workflows_list_versions(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        workflow_id = random_hex(10)
        mock_workflow_version_list(respx_mock, workflow_id)
        paged = coze.workflows.versions.list(workflow_id=workflow_id)
        items = list(paged)
        assert len(items) == 2
        assert items[0].version
        assert items[1].version

    def test_sync_workflows_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        workflow_id = random_hex(10)
        mock_workflow_retrieve(respx_mock, workflow_id)

        res = coze.workflows.retrieve(workflow_id=workflow_id)
        assert res
        workflow_basic = res.workflow_detail
        assert workflow_basic.workflow_id == workflow_id
        assert workflow_basic.workflow_name
        assert workflow_basic.description
        assert workflow_basic.icon_url
        assert workflow_basic.app_id
        assert workflow_basic.created_at
        assert workflow_basic.updated_at


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncWorkflows:
    async def test_sync_workflows_list(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        mock_workflow_list(respx_mock)
        paged = await coze.workflows.list(page_num=1, page_size=2)
        items = [item async for item in paged]
        assert len(items) == 2
        assert items[0].workflow_id == "w1"
        assert items[1].workflow_id == "w2"

    async def test_sync_workflows_list_versions(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        workflow_id = random_hex(10)
        mock_workflow_version_list(respx_mock, workflow_id)
        paged = await coze.workflows.versions.list(workflow_id=workflow_id)
        items = [item async for item in paged]
        assert len(items) == 2
        assert items[0].version
        assert items[1].version

    async def test_sync_workflows_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        workflow_id = random_hex(10)
        mock_workflow_retrieve(respx_mock, workflow_id)

        res = await coze.workflows.retrieve(workflow_id=workflow_id)
        assert res
        workflow_basic = res.workflow_detail
        assert workflow_basic.workflow_id == workflow_id
        assert workflow_basic.workflow_name
        assert workflow_basic.description
        assert workflow_basic.icon_url
        assert workflow_basic.app_id
        assert workflow_basic.created_at
        assert workflow_basic.updated_at
