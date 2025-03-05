import warnings

import httpx
import pytest

from cozepy import (
    AsyncCoze,
    AsyncTokenAuth,
    Coze,
    Document,
    DocumentBase,
    DocumentChunkStrategy,
    DocumentFormatType,
    DocumentSourceInfo,
    DocumentSourceType,
    DocumentStatus,
    DocumentUpdateRule,
    DocumentUpdateType,
    TokenAuth,
)
from cozepy.util import random_hex
from tests.test_util import logid_key


@pytest.fixture(autouse=True)
def ignore_warnings():
    warnings.simplefilter("ignore", DeprecationWarning)
    yield
    warnings.resetwarnings()


def make_document(id: int = 0) -> Document:
    return Document.model_validate(
        {
            "document_id": f"id_{id}" if id else "id",
            "char_count": 1,
            "create_time": 1,
            "update_time": 1,
            "format_type": DocumentFormatType.DOCUMENT,
            "hit_count": 1,
            "name": "str",
            "size": 1,
            "slice_count": 1,
            "source_type": DocumentSourceType.LOCAL_FILE,
            "status": DocumentStatus.FAILED,
            "type": "str",
            "update_interval": 1,
            "update_type": DocumentUpdateType.AUTO_UPDATE,
        }
    )


def mock_create_datasets_documents(respx_mock) -> Document:
    document = make_document()
    document._raw_response = httpx.Response(
        200,
        json={"document_infos": [document.model_dump()]},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.post("/open_api/knowledge/document/create").mock(document._raw_response)
    return document


def mock_update_datasets_documents(respx_mock) -> Document:
    document = make_document()
    document._raw_response = httpx.Response(
        200,
        json={"data": None},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.post("/open_api/knowledge/document/update").mock(document._raw_response)
    return document


def mock_delete_datasets_documents(respx_mock) -> Document:
    document = make_document()
    document._raw_response = httpx.Response(
        200,
        json={"data": None},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.post("/open_api/knowledge/document/delete").mock(document._raw_response)
    return document


def mock_list_datasets_documents(respx_mock, total_count, page):
    respx_mock.post(
        "/open_api/knowledge/document/list",
        json={
            "dataset_id": "id",
            "page": page,
            "size": 1,
        },
    ).mock(
        httpx.Response(
            200,
            json={
                "data": {
                    "total": total_count,
                    "document_infos": [make_document(page).model_dump()],
                }
            },
        )
    )


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncDatasetsDocuments:
    def test_sync_datasets_documents_create_web_auto_update(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_document = mock_create_datasets_documents(respx_mock)

        documents = coze.datasets.documents.create(
            dataset_id="dataset_id",
            document_bases=[
                DocumentBase(
                    name="name",
                    source_info=DocumentSourceInfo.build_web_page("x"),
                    update_rule=DocumentUpdateRule.build_auto_update(1),
                ),
            ],
            chunk_strategy=DocumentChunkStrategy.build_auto(),
        )
        assert documents
        assert documents.response.logid == mock_document.response.logid
        assert len(documents) == 1

    def test_sync_datasets_documents_create_local_custom(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_document = mock_create_datasets_documents(respx_mock)

        documents = coze.datasets.documents.create(
            dataset_id="dataset_id",
            document_bases=[
                DocumentBase(
                    name="name",
                    source_info=DocumentSourceInfo.build_local_file("content"),
                    update_rule=DocumentUpdateRule.build_no_auto_update(),
                ),
            ],
            chunk_strategy=DocumentChunkStrategy.build_custom(1, ",", False, True),
        )
        assert documents
        assert documents.response.logid == mock_document.response.logid
        assert len(documents) == 1

    def test_sync_datasets_documents_update(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_document = mock_update_datasets_documents(respx_mock)

        res = coze.datasets.documents.update(document_id="id", document_name="name")
        assert res
        assert res.response.logid == mock_document.response.logid

    def test_sync_datasets_documents_delete(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_document = mock_delete_datasets_documents(respx_mock)

        res = coze.datasets.documents.delete(document_ids=["id"])
        assert res
        assert res.response.logid == mock_document.response.logid

    def test_sync_datasets_documents_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        total = 10
        size = 1
        for idx in range(total):
            mock_list_datasets_documents(respx_mock, total_count=total, page=idx + 1)

        # no iter
        resp = coze.datasets.documents.list(dataset_id="id", page_num=1, page_size=1)
        assert resp
        assert resp.has_more is True

        # iter dataset
        total_result = 0
        for message in resp:
            total_result += 1
            assert message
            assert message.document_id == f"id_{total_result}"
        assert total_result == total

        # iter page
        total_result = 0
        for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.has_more == (total_result < total)
            assert len(page.items) == size
            document = page.items[0]
            assert document.document_id == f"id_{total_result}"
        assert total_result == total


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncDatasetsDocuments:
    async def test_async_datasets_documents_create_web_auto_update(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_document = mock_create_datasets_documents(respx_mock)

        documents = await coze.datasets.documents.create(
            dataset_id="dataset_id",
            document_bases=[
                DocumentBase(
                    name="name",
                    source_info=DocumentSourceInfo.build_web_page("x"),
                    update_rule=DocumentUpdateRule.build_auto_update(1),
                ),
            ],
            chunk_strategy=DocumentChunkStrategy.build_auto(),
        )
        assert documents
        assert documents.response.logid == mock_document.response.logid
        assert len(documents) == 1

    async def test_async_datasets_documents_create_local_custom(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_document = mock_create_datasets_documents(respx_mock)

        documents = await coze.datasets.documents.create(
            dataset_id="dataset_id",
            document_bases=[
                DocumentBase(
                    name="name",
                    source_info=DocumentSourceInfo.build_local_file("content"),
                    update_rule=DocumentUpdateRule.build_no_auto_update(),
                ),
            ],
            chunk_strategy=DocumentChunkStrategy.build_custom(1, ",", False, True),
        )
        assert documents
        assert documents.response.logid == mock_document.response.logid
        assert len(documents) == 1

    async def test_async_datasets_documents_update(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_document = mock_update_datasets_documents(respx_mock)

        res = await coze.datasets.documents.update(document_id="id", document_name="name")
        assert res
        assert res.response.logid == mock_document.response.logid

    async def test_async_datasets_documents_delete(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_document = mock_delete_datasets_documents(respx_mock)

        res = await coze.datasets.documents.delete(document_ids=["id"])
        assert res
        assert res.response.logid == mock_document.response.logid

    async def test_async_datasets_documents_list(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        total = 10
        size = 1
        for idx in range(total):
            mock_list_datasets_documents(respx_mock, total_count=total, page=idx + 1)

        # no iter
        resp = await coze.datasets.documents.list(dataset_id="id", page_num=1, page_size=1)
        assert resp
        assert resp.has_more is True

        # iter dataset
        total_result = 0
        async for message in resp:
            total_result += 1
            assert message
            assert message.document_id == f"id_{total_result}"
        assert total_result == total

        # iter page
        total_result = 0
        async for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.has_more == (total_result < total)
            assert len(page.items) == size
            document = page.items[0]
            assert document.document_id == f"id_{total_result}"
        assert total_result == total
