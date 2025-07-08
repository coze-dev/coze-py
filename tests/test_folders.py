import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Coze, FolderType, SimpleFolder, TokenAuth
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_list_folders(respx_mock, total_count, page):
    logid = random_hex(10)
    respx_mock.get(
        "/v1/folders",
        params={
            "page_num": page,
            "folder_type": FolderType.DEVELOPMENT.value,
            "workspace_id": "workspace_id",
        },
    ).mock(
        httpx.Response(
            200,
            json={
                "data": {
                    "items": [
                        SimpleFolder(
                            id=f"id_{page}",
                            name=random_hex(10),
                            description=random_hex(10),
                            workspace_id=random_hex(10),
                            creator_user_id=random_hex(10),
                            parent_folder_id=random_hex(10),
                        ).model_dump()
                    ],
                    "total_count": total_count,
                }
            },
            headers={logid_key(): logid},
        )
    )
    return logid


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncFolders:
    def test_sync_folders_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        workspace_id = "workspace_id"
        total = 5
        size = 1
        for idx in range(total):
            mock_list_folders(respx_mock, total_count=total, page=idx + 1)

        resp = coze.folders.list(workspace_id=workspace_id, folder_type=FolderType.DEVELOPMENT, page_num=1, page_size=1)
        assert resp
        assert resp.has_more is True

        total_result = 0
        for folder in resp:
            total_result += 1
            assert folder
            assert folder.id == f"id_{total_result}"
        assert total_result == total

        total_result = 0
        for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.has_more == (total_result < total)
            assert len(page.items) == size
            folder = page.items[0]
            assert folder.id == f"id_{total_result}"
        assert total_result == total


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncFolders:
    async def test_async_folders_list(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        workspace_id = "workspace_id"
        total = 5
        size = 1
        for idx in range(total):
            mock_list_folders(respx_mock, total_count=total, page=idx + 1)

        resp = await coze.folders.list(
            workspace_id=workspace_id, folder_type=FolderType.DEVELOPMENT, page_num=1, page_size=1
        )
        assert resp
        assert resp.has_more is True

        total_result = 0
        async for folder in resp:
            total_result += 1
            assert folder
            assert folder.id == f"id_{total_result}"
        assert total_result == total

        total_result = 0
        async for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.has_more == (total_result < total)
            assert len(page.items) == size
            folder = page.items[0]
            assert folder.id == f"id_{total_result}"
        assert total_result == total
