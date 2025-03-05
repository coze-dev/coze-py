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


def mock_documents_list(respx_mock, total, page):
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
                    "total": total,
                    "document_infos": [make_document(page).model_dump()],
                }
            },
        )
    )


@pytest.mark.respx(base_url="https://api.coze.com")
class TestKnowledgeDocuments:
    def test_create_web_auto_update(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/open_api/knowledge/document/create").mock(
            httpx.Response(
                200,
                json={"document_infos": [make_document().model_dump()]},
            )
        )

        documents = coze.knowledge.documents.create(
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
        assert len(documents) == 1

    def test_create_local_custom(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/open_api/knowledge/document/create").mock(
            httpx.Response(
                200,
                json={"document_infos": [make_document().model_dump()]},
            )
        )

        documents = coze.knowledge.documents.create(
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
        assert len(documents) == 1

    def test_update(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/open_api/knowledge/document/update").mock(httpx.Response(200, json={"data": None}))

        coze.knowledge.documents.update(document_id="id", document_name="name")

    def test_knowledge_documents_delete(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/open_api/knowledge/document/delete").mock(httpx.Response(200, json={"data": None}))

        coze.knowledge.documents.delete(document_ids=["id"])

    def test_sync_knowledge_documents_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/open_api/knowledge/document/list").mock(
            httpx.Response(
                200,
                json={
                    "data": {
                        "total": 1,
                        "document_infos": [make_document().model_dump()],
                    }
                },
            )
        )

        res = coze.knowledge.documents.list(dataset_id="id")
        assert res
        assert res.total == 1

    def test_sync_knowledge_documents_iterator(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        total = 10
        size = 1
        for idx in range(total):
            respx_mock.post(
                "/open_api/knowledge/document/list",
                json={
                    "dataset_id": "id",
                    "page": idx + 1,
                    "size": size,
                },
            ).mock(
                httpx.Response(
                    200,
                    json={
                        "data": {
                            "total": total,
                            "document_infos": [make_document(idx + 1).model_dump()],
                        }
                    },
                )
            )

        total_result = 0
        for idx, document in enumerate(coze.knowledge.documents.list(dataset_id="id", page_size=size)):
            total_result += 1
            assert document
            assert document.document_id == f"id_{idx + 1}"
        assert total_result == total

    def test_sync_knowledge_documents_page_iterator(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        total = 10
        size = 1
        for idx in range(total):
            respx_mock.post(
                "/open_api/knowledge/document/list",
                json={
                    "dataset_id": "id",
                    "page": idx + 1,
                    "size": size,
                },
            ).mock(
                httpx.Response(
                    200,
                    json={
                        "data": {
                            "total": total,
                            "document_infos": [make_document(idx + 1).model_dump()],
                        }
                    },
                )
            )

        total_result = 0
        for idx, page in enumerate(coze.knowledge.documents.list(dataset_id="id", page_size=size).iter_pages()):
            total_result += 1
            assert page
            assert page.total == total
            assert len(page.items) == size
            document = page.items[0]
            assert document.document_id == f"id_{idx + 1}"
        assert total_result == total


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncKnowledgeDocuments:
    async def test_sync_knowledge_documents_create_web_auto_update(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        respx_mock.post("/open_api/knowledge/document/create").mock(
            httpx.Response(
                200,
                json={"document_infos": [make_document().model_dump()]},
            )
        )

        documents = await coze.knowledge.documents.create(
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
        assert len(documents) == 1

    async def test_sync_knowledge_documents_create_local_custom(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        respx_mock.post("/open_api/knowledge/document/create").mock(
            httpx.Response(
                200,
                json={"document_infos": [make_document().model_dump()]},
            )
        )

        documents = await coze.knowledge.documents.create(
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
        assert len(documents) == 1

    async def test_sync_knowledge_documents_update(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        respx_mock.post("/open_api/knowledge/document/update").mock(httpx.Response(200, json={"data": None}))

        await coze.knowledge.documents.update(document_id="id", document_name="name")

    async def test_sync_knowledge_documents_delete(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        respx_mock.post("/open_api/knowledge/document/delete").mock(httpx.Response(200, json={"data": None}))

        await coze.knowledge.documents.delete(document_ids=["id"])

    async def test_sync_knowledge_documents_list(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        total = 10
        mock_documents_list(respx_mock, total, 1)

        resp = await coze.knowledge.documents.list(dataset_id="id", page_num=1, page_size=1)
        assert resp
        assert resp.total == total

    async def test_async_knowledge_documents_iterator(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        total = 10
        for idx in range(total):
            mock_documents_list(respx_mock, total, idx + 1)

        resp = await coze.knowledge.documents.list(dataset_id="id", page_num=1, page_size=1)

        total_result = 0
        async for document in resp:
            total_result += 1
            assert document
            assert document.document_id == f"id_{total_result}"
        assert total_result == total

    async def test_async_knowledge_documents_page_iterator(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        total = 10
        for idx in range(total):
            mock_documents_list(respx_mock, total, idx + 1)

        resp = await coze.knowledge.documents.list(dataset_id="id", page_num=1, page_size=1)

        total_result = 0
        async for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.total == total
            assert len(page.items) == 1
            document = page.items[0]
            assert document.document_id == f"id_{total_result}"
        assert total_result == total
