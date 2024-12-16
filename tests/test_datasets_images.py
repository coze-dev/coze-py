import httpx
import pytest

from cozepy import (
    AsyncCoze,
    Coze,
    TokenAuth,
)
from cozepy.util import random_hex


def mock_datasets_images_update(respx_mock, dataset_id: str, document_id: str):
    respx_mock.put(f"/v1/datasets/{dataset_id}/images/{document_id}").mock(httpx.Response(200, json={"data": None}))


@pytest.mark.respx(base_url="https://api.coze.com")
class TestDatasetsImages:
    def test_sync_datasets_images_update(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        dataset_id = random_hex(10)
        document_id = random_hex(10)

        mock_datasets_images_update(respx_mock, dataset_id, document_id)

        coze.datasets.images.update(dataset_id=dataset_id, document_id=document_id, caption="caption")


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncDatasetsDocuments:
    async def test_async_datasets_images_update(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        dataset_id = random_hex(10)
        document_id = random_hex(10)

        mock_datasets_images_update(respx_mock, dataset_id, document_id)

        await coze.datasets.images.update(dataset_id=dataset_id, document_id=document_id, caption="caption")
