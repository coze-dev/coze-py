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
                            enterprise_id="",
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

    def test_sync_workspaces_list_with_user_id_and_coze_account_id(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        total = 2
        size = 1
        user_id = "user_id"
        coze_account_id = "coze_account_id"
        for idx in range(total):
            respx_mock.get(
                "/v1/workspaces",
                params={
                    "page_num": idx + 1,
                    "page_size": size,
                    "user_id": user_id,
                    "coze_account_id": coze_account_id,
                },
            ).mock(
                httpx.Response(
                    200,
                    json={
                        "data": {
                            "total_count": total,
                            "workspaces": [
                                Workspace(
                                    id=f"id_{idx+1}",
                                    name="name",
                                    icon_url="icon_url",
                                    role_type=WorkspaceRoleType.ADMIN,
                                    workspace_type=WorkspaceType.PERSONAL,
                                    enterprise_id="",
                                ).model_dump()
                            ],
                        }
                    },
                )
            )

        resp = coze.workspaces.list(page_num=1, page_size=1, user_id=user_id, coze_account_id=coze_account_id)
        assert resp
        assert resp.has_more is True
        total_result = 0
        for workspace in resp:
            total_result += 1
            assert workspace
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

    async def test_async_workspaces_list_with_user_id_and_coze_account_id(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        total = 2
        size = 1
        user_id = "user_id"
        coze_account_id = "coze_account_id"
        for idx in range(total):
            respx_mock.get(
                "/v1/workspaces",
                params={
                    "page_num": idx + 1,
                    "page_size": size,
                    "user_id": user_id,
                    "coze_account_id": coze_account_id,
                },
            ).mock(
                httpx.Response(
                    200,
                    json={
                        "data": {
                            "total_count": total,
                            "workspaces": [
                                Workspace(
                                    id=f"id_{idx+1}",
                                    name="name",
                                    icon_url="icon_url",
                                    role_type=WorkspaceRoleType.ADMIN,
                                    workspace_type=WorkspaceType.PERSONAL,
                                    enterprise_id="",
                                ).model_dump()
                            ],
                        }
                    },
                )
            )

        resp = await coze.workspaces.list(page_num=1, page_size=1, user_id=user_id, coze_account_id=coze_account_id)
        assert resp
        assert resp.has_more is True
        total_result = 0
        async for workspace in resp:
            total_result += 1
            assert workspace
            assert workspace.id == f"id_{total_result}"
        assert total_result == total
