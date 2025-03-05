import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Coze, TokenAuth, Workspace, WorkspaceRoleType, WorkspaceType


def mock_list_workspaces(respx_mock, total_count, page):
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
                    "total_count": total_count,
                    "workspaces": [
                        Workspace(
                            id=f"id_{page}" if page else "id",
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
class TestSyncWorkspaces:
    def test_sync_workspaces_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        total = 10
        size = 1
        for idx in range(total):
            mock_list_workspaces(respx_mock, total_count=total, page=idx + 1)

        # no iter
        resp = coze.workspaces.list(page_num=1, page_size=1)
        assert resp
        assert resp.has_more is True

        # iter
        total_result = 0
        for workspace in resp:
            total_result += 1
            assert workspace
            assert workspace.id == f"id_{total_result}"
        assert total_result == total

        # iter page
        total_result = 0
        for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.has_more == (total_result < total)
            assert len(page.items) == size
            workspace = page.items[0]
            assert workspace.id == f"id_{total_result}"
        assert total_result == total


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncWorkspaces:
    async def test_async_workspaces_list(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        total = 10
        size = 1
        for idx in range(total):
            mock_list_workspaces(respx_mock, total_count=total, page=idx + 1)

        # no iter
        resp = await coze.workspaces.list(page_num=1, page_size=1)
        assert resp
        assert resp.has_more is True

        # iter
        total_result = 0
        async for workspace in resp:
            total_result += 1
            assert workspace
            assert workspace.id == f"id_{total_result}"
        assert total_result == total

        # iter page
        total_result = 0
        async for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.has_more == (total_result < total)
            assert len(page.items) == size
            workspace = page.items[0]
            assert workspace.id == f"id_{total_result}"
        assert total_result == total
