import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Coze, TokenAuth
from cozepy.datasets import Dataset, DatasetStatus, DocumentFormatType, DocumentProgress
from cozepy.datasets.documents import DocumentStatus, DocumentUpdateType
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_create_datasets(respx_mock):
    dataset_id = random_hex(10)
    logid = random_hex(10)
    respx_mock.post("/v1/datasets").mock(
        httpx.Response(
            200,
            json={"data": {"dataset_id": dataset_id}},
            headers={logid_key(): logid},
        )
    )
    return dataset_id, logid


def mock_list_dataset(respx_mock, total_count, page):
    respx_mock.get(
        "/v1/datasets",
        params={
            "page_num": page,
        },
    ).mock(
        httpx.Response(
            200,
            headers={logid_key(): "logid"},
            json={
                "data": {
                    "dataset_list": [
                        Dataset(
                            dataset_id=f"id_{page}",
                            name=f"name_{page}",
                            description=f"description_{page}",
                            space_id=f"space_id_{page}",
                            status=DatasetStatus.ENABLED,
                            format_type=DocumentFormatType.DOCUMENT,
                        ).model_dump()
                    ],
                    "total_count": total_count,
                }
            },
        )
    )


def mock_update_datasets(respx_mock):
    dataset_id = random_hex(10)
    logid = random_hex(10)
    respx_mock.put(f"/v1/datasets/{dataset_id}").mock(
        httpx.Response(
            200,
            json={"data": {}},
            headers={logid_key(): logid},
        )
    )
    return dataset_id, logid


def mock_delete_datasets(respx_mock):
    dataset_id = random_hex(10)
    logid = random_hex(10)
    respx_mock.delete(f"/v1/datasets/{dataset_id}").mock(
        httpx.Response(
            200,
            json={"data": {}},
            headers={logid_key(): logid},
        )
    )
    return dataset_id, logid


def mock_process_datasets(
    respx_mock,
):
    dataset_id = random_hex(10)
    document_id = random_hex(10)
    logid = random_hex(10)
    respx_mock.post(f"/v1/datasets/{dataset_id}/process").mock(
        httpx.Response(
            200,
            json={
                "data": {
                    "data": [
                        DocumentProgress(
                            document_id=document_id,
                            document_name="document_name",
                            status=DocumentStatus.PROCESSING,
                            update_type=DocumentUpdateType.AUTO_UPDATE,
                            progress=0,
                            remaining_time=0,
                        ).model_dump()
                    ]
                }
            },
            headers={logid_key(): logid},
        )
    )
    return dataset_id, document_id, logid


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncDataset:
    def test_sync_datasets_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        dataset_id, mock_logid = mock_create_datasets(respx_mock)

        dataset = coze.datasets.create(space_id="space id", name="name", format_type=DocumentFormatType.DOCUMENT)
        assert dataset
        assert dataset.response.logid == mock_logid
        assert dataset.dataset_id == dataset_id

    def test_sync_datasets_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        space_id = random_hex(10)
        total = 10
        size = 1
        for idx in range(total):
            mock_list_dataset(respx_mock, total_count=total, page=idx + 1)

        # no iter
        resp = coze.datasets.list(space_id=space_id, page_num=1, page_size=1)
        assert resp
        assert resp.has_more is True

        # iter dataset
        total_result = 0
        for dataset in resp:
            total_result += 1
            assert dataset
            assert dataset.dataset_id == f"id_{total_result}"
        assert total_result == total

        # iter page
        total_result = 0
        for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.has_more == (total_result < total)
            assert len(page.items) == size
            dataset = page.items[0]
            assert dataset.dataset_id == f"id_{total_result}"
        assert total_result == total

    def test_sync_datasets_update(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        dataset_id, mock_logid = mock_update_datasets(respx_mock)

        res = coze.datasets.update(dataset_id=dataset_id, name="name")
        assert res
        assert res.response.logid == mock_logid

    def test_sync_datasets_delete(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        dataset_id, mock_logid = mock_delete_datasets(respx_mock)

        res = coze.datasets.delete(dataset_id=dataset_id)
        assert res
        assert res.response.logid == mock_logid

    def test_sync_datasets_process(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        dataset_id, document_id, mock_logid = mock_process_datasets(respx_mock)

        res = coze.datasets.process(dataset_id=dataset_id, document_ids=[document_id])
        assert res
        assert res.response.logid == mock_logid


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncDataset:
    async def test_async_datasets_create(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        dataset_id, mock_logid = mock_create_datasets(respx_mock)

        dataset = await coze.datasets.create(space_id="space id", name="name", format_type=DocumentFormatType.DOCUMENT)
        assert dataset
        assert dataset.response.logid == mock_logid
        assert dataset.dataset_id == dataset_id

    async def test_async_datasets_list(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        space_id = random_hex(10)
        total = 10
        size = 1
        for idx in range(total):
            mock_list_dataset(respx_mock, total_count=total, page=idx + 1)

        # no iter
        resp = await coze.datasets.list(space_id=space_id, page_num=1, page_size=1)
        assert resp
        assert resp.has_more is True

        # iter dataset
        total_result = 0
        async for dataset in resp:
            total_result += 1
            assert dataset
            assert dataset.dataset_id == f"id_{total_result}"
        assert total_result == total

        # iter page
        total_result = 0
        async for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.has_more == (total_result < total)
            assert len(page.items) == size
            dataset = page.items[0]
            assert dataset.dataset_id == f"id_{total_result}"
        assert total_result == total

    async def test_async_datasets_update(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        dataset_id, mock_logid = mock_update_datasets(respx_mock)

        res = await coze.datasets.update(dataset_id=dataset_id, name="name")
        assert res
        assert res.response.logid == mock_logid

    async def test_async_datasets_delete(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        dataset_id, mock_logid = mock_delete_datasets(respx_mock)

        res = await coze.datasets.delete(dataset_id=dataset_id)
        assert res
        assert res.response.logid == mock_logid

    async def test_async_datasets_process(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        dataset_id, document_id, mock_logid = mock_process_datasets(respx_mock)

        res = await coze.datasets.process(dataset_id=dataset_id, document_ids=[document_id])
        assert res
        assert res.response.logid == mock_logid
