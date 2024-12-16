import httpx
import pytest

from cozepy import AsyncCoze, Coze, TokenAuth
from cozepy.datasets import Dataset, DatasetFormatType, DatasetStatus
from cozepy.util import random_hex


def mock_create_dataset(respx_mock, dataset_id):
    respx_mock.post("/v1/datasets").mock(
        httpx.Response(
            200,
            json={"data": {"dataset_id": dataset_id}},
        )
    )


def mock_list_dataset(respx_mock, total_count, page):
    respx_mock.get(
        "https://api.coze.com/v1/datasets",
        params={
            "page_num": page,
        },
    ).mock(
        httpx.Response(
            200,
            headers={"x-tt-logid": "logid"},
            json={
                "data": {
                    "dataset_list": [
                        Dataset(
                            dataset_id=f"id_{page}",
                            name=f"name_{page}",
                            description=f"description_{page}",
                            space_id=f"space_id_{page}",
                            status=DatasetStatus.ENABLED,
                            format_type=DatasetFormatType.TEXT,
                        ).model_dump()
                    ],
                    "total_count": total_count,
                }
            },
        )
    )


def mock_update_dataset(respx_mock, dataset_id):
    respx_mock.put(f"/v1/datasets/{dataset_id}").mock(
        httpx.Response(
            200,
            json={"data": {}},
        )
    )


def mock_delete_dataset(respx_mock, dataset_id):
    respx_mock.delete(f"/v1/datasets/{dataset_id}").mock(
        httpx.Response(
            200,
            json={"data": {}},
        )
    )


@pytest.mark.respx(base_url="https://api.coze.com")
class TestDataset:
    def test_sync_dataset_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        dataset_id = random_hex(10)
        mock_create_dataset(respx_mock, dataset_id)

        dataset = coze.datasets.create(space_id="space id", name="name", format_type=DatasetFormatType.TEXT)
        assert dataset
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
        for idx, dataset in enumerate(coze.datasets.list(space_id=space_id, page_num=1, page_size=1)):
            total_result += 1
            assert dataset
            assert dataset.dataset_id == f"id_{idx + 1}"
        assert total_result == total

        # iter page
        total_result = 0
        for idx, page in enumerate(coze.datasets.list(space_id=space_id, page_num=1, page_size=1).iter_pages()):
            total_result += 1
            assert page
            assert page.has_more == (idx + 1 < total)
            assert len(page.items) == size
            dataset = page.items[0]
            assert dataset.dataset_id == f"id_{idx + 1}"
        assert total_result == total

    def test_sync_dataset_update(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        dataset_id = random_hex(10)
        mock_update_dataset(respx_mock, dataset_id)

        coze.datasets.update(dataset_id=dataset_id, name="name")

    def test_sync_dataset_delete(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        dataset_id = random_hex(10)
        mock_delete_dataset(respx_mock, dataset_id)

        coze.datasets.delete(dataset_id=dataset_id)


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncDataset:
    async def test_async_dataset_create(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        dataset_id = random_hex(10)
        mock_create_dataset(respx_mock, dataset_id)

        dataset = await coze.datasets.create(space_id="space id", name="name", format_type=DatasetFormatType.TEXT)
        assert dataset
        assert dataset.dataset_id == dataset_id

    async def test_async_datasets_list(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

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

    async def test_async_dataset_update(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        dataset_id = random_hex(10)
        mock_update_dataset(respx_mock, dataset_id)

        await coze.datasets.update(dataset_id=dataset_id, name="name")

    async def test_async_dataset_delete(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        dataset_id = random_hex(10)
        mock_delete_dataset(respx_mock, dataset_id)

        await coze.datasets.delete(dataset_id=dataset_id)
