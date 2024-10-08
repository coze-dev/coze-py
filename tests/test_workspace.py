import httpx
import pytest

from cozepy import AsyncCoze, Coze, TokenAuth, Workspace, WorkspaceRoleType, WorkspaceType


@pytest.mark.respx(base_url="https://api.coze.com")
class TestWorkspace:
    def test_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.get("/v1/workspaces").mock(
            httpx.Response(
                200,
                json={
                    "data": {
                        "total_count": 1,
                        "workspaces": [
                            Workspace(
                                id="id",
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

        res = coze.workspaces.list()

        assert res
        assert res.items[0].id == "id"


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncWorkspace:
    async def test_list(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.get("/v1/workspaces").mock(
            httpx.Response(
                200,
                json={
                    "data": {
                        "total_count": 1,
                        "workspaces": [
                            Workspace(
                                id="id",
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

        res = await coze.workspaces.list()

        assert res
        assert res.items[0].id == "id"
