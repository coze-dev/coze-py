import httpx
import pytest

from cozepy import AsyncCoze, Coze, TokenAuth, Workspace, WorkspaceRoleType, WorkspaceType


def mock_get_workspace_list(respx_mock, total, page, idx):
    respx_mock.get(
        "/v1/workspaces",
        params={
            "page_num": page,
        },
    ).mock(
        httpx.Response(
            200,
            json={
                "data": {
                    "total_count": total,
                    "workspaces": [
                        Workspace(
                            id=f"id_{idx}" if idx else "id",
                            name="name",
                            icon_url="icon_url",
                            role_type=WorkspaceRoleType.ADMIN,
                            workspace_type=WorkspaceType.PERSONAL,
                        ).model_dump()
                    ],
                }
            },
        )
    )


@pytest.mark.respx(base_url="https://api.coze.com")
class TestWorkspace:
    def test_sync_workspaces_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_get_workspace_list(respx_mock, total=1, page=1, idx=0)

        res = coze.workspaces.list()

        assert res
        assert res.items[0].id == "id"

    def test_sync_workspaces_iterator(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        total = 10
        for idx in range(total):
            mock_get_workspace_list(respx_mock, total=total, page=idx + 1, idx=idx + 1)

        total_result = 0
        for idx, workspace in enumerate(coze.workspaces.list(page_size=1)):
            total_result += 1
            assert workspace
            assert workspace.id == f"id_{idx + 1}"
        assert total_result == total

    def test_sync_workspaces_page_iterator(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        total = 10
        size = 1
        for idx in range(total):
            mock_get_workspace_list(respx_mock, total=total, page=idx + 1, idx=idx + 1)

        total_result = 0
        for idx, page in enumerate(coze.workspaces.list(page_size=1).iter_pages()):
            total_result += 1
            assert page
            assert page.total == total
            assert len(page.items) == size
            workspace = page.items[0]
            assert workspace.id == f"id_{idx + 1}"
        assert total_result == total


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncWorkspace:
    async def test_async_workspaces_list(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        mock_get_workspace_list(respx_mock, total=1, page=1, idx=0)

        res = await coze.workspaces.list(page_num=1)

        assert res
        assert res.items[0].id == "id"

    async def test_async_workspaces_iterator(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        total = 10
        for idx in range(total):
            mock_get_workspace_list(respx_mock, total=total, page=idx + 1, idx=idx + 1)

        total_result = 0
        idx = 0
        async for workspace in await coze.workspaces.list(page_size=1):
            assert workspace
            assert workspace.id == f"id_{idx + 1}"
            idx += 1
            total_result += 1
        assert total_result == total

    async def test_async_workspaces_page_iterator(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        total = 10
        for idx in range(total):
            mock_get_workspace_list(respx_mock, total=total, page=idx + 1, idx=idx + 1)

        total_result = 0
        idx = 0
        resp = await coze.workspaces.list(page_size=1)
        async for page in resp.iter_pages():
            assert page
            workspace = page.items[0]
            assert workspace
            assert workspace.id == f"id_{idx + 1}"
            idx += 1
            total_result += 1
        assert total_result == total
