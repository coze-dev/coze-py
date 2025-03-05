import httpx
import pytest

from cozepy import (
    AsyncCoze,
    AsyncTokenAuth,
    Coze,
    TokenAuth,
)
from cozepy.datasets.documents import DocumentSourceType
from cozepy.datasets.images import Photo, PhotoStatus
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_update_datasets_images(respx_mock):
    dataset_id = random_hex(10)
    document_id = random_hex(10)
    logid = random_hex(10)
    respx_mock.put(f"/v1/datasets/{dataset_id}/images/{document_id}").mock(
        httpx.Response(
            200,
            headers={logid_key(): logid},
            json={"data": None},
        )
    )
    return dataset_id, document_id, logid


def mock_list_dataset_images(respx_mock, dataset_id, total_count, page):
    respx_mock.get(
        f"https://api.coze.com/v1/datasets/{dataset_id}/images",
        params={
            "page_num": page,
        },
    ).mock(
        httpx.Response(
            200,
            headers={logid_key(): "logid"},
            json={
                "data": {
                    "photo_infos": [
                        Photo(
                            document_id=f"id_{page}",
                            status=PhotoStatus.COMPLETED,
                            source_type=DocumentSourceType.UPLOAD_FILE_ID,
                        ).model_dump()
                    ],
                    "total_count": total_count,
                }
            },
        )
    )


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncDatasetsImages:
    def test_sync_datasets_images_update(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        dataset_id, document_id, mock_logid = mock_update_datasets_images(respx_mock)

        res = coze.datasets.images.update(dataset_id=dataset_id, document_id=document_id, caption="caption")
        assert res
        assert res.response.logid == mock_logid

    def test_sync_datasets_images_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        dataset_id = random_hex(10)
        total = 10
        size = 1
        for idx in range(total):
            mock_list_dataset_images(respx_mock, dataset_id, total_count=total, page=idx + 1)

        # no iter
        resp = coze.datasets.images.list(dataset_id=dataset_id, page_num=1, page_size=1)
        assert resp
        assert resp.has_more is True

        # iter dataset
        total_result = 0
        for dataset in resp:
            total_result += 1
            assert dataset
            assert dataset.document_id == f"id_{total_result}"
        assert total_result == total

        # iter page
        total_result = 0
        for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.has_more == (total_result < total)
            assert len(page.items) == size
            dataset = page.items[0]
            assert dataset.document_id == f"id_{total_result}"
        assert total_result == total


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncDatasetsDocuments:
    async def test_sync_datasets_images_update(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        dataset_id, document_id, mock_logid = mock_update_datasets_images(respx_mock)

        res = await coze.datasets.images.update(dataset_id=dataset_id, document_id=document_id, caption="caption")
        assert res
        assert res.response.logid == mock_logid

    async def test_sync_datasets_images_list(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        dataset_id = random_hex(10)
        total = 10
        size = 1
        for idx in range(total):
            mock_list_dataset_images(respx_mock, dataset_id, total_count=total, page=idx + 1)

        # no iter
        resp = await coze.datasets.images.list(dataset_id=dataset_id, page_num=1, page_size=1)
        assert resp
        assert resp.has_more is True

        # iter dataset
        total_result = 0
        async for dataset in resp:
            total_result += 1
            assert dataset
            assert dataset.document_id == f"id_{total_result}"
        assert total_result == total

        # iter page
        total_result = 0
        async for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.has_more == (total_result < total)
            assert len(page.items) == size
            dataset = page.items[0]
            assert dataset.document_id == f"id_{total_result}"
        assert total_result == total
