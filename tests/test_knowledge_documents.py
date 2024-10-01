import httpx
import pytest

from cozepy import (
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

document_testdata = Document.model_validate(
    {
        "document_id": "str",
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


@pytest.mark.respx(base_url="https://api.coze.com")
class TestKnowledgeDocuments:
    def test_create_web_auto_update(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/open_api/knowledge/document/create").mock(
            httpx.Response(
                200,
                json={"document_infos": [document_testdata.model_dump()]},
            )
        )

        documents = coze.knowledge.documents.create(
            dataset_id="dataset_id",
            document_bases=[
                DocumentBase(
                    name="name",
                    source_info=DocumentSourceInfo.from_web_page("x"),
                    update_rule=DocumentUpdateRule.auto_update(1),
                ),
            ],
            chunk_strategy=DocumentChunkStrategy.auto(),
        )
        assert documents
        assert len(documents) == 1

    def test_create_local_custom(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/open_api/knowledge/document/create").mock(
            httpx.Response(
                200,
                json={"document_infos": [document_testdata.model_dump()]},
            )
        )

        documents = coze.knowledge.documents.create(
            dataset_id="dataset_id",
            document_bases=[
                DocumentBase(
                    name="name",
                    source_info=DocumentSourceInfo.from_local_file("content"),
                    update_rule=DocumentUpdateRule.no_auto_update(),
                ),
            ],
            chunk_strategy=DocumentChunkStrategy.custom(1, ",", False, True),
        )
        assert documents
        assert len(documents) == 1

    def test_update(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/open_api/knowledge/document/update").mock(httpx.Response(200, json={"data": None}))

        coze.knowledge.documents.update(document_id="id", document_name="name")

    def test_delete(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/open_api/knowledge/document/delete").mock(httpx.Response(200, json={"data": None}))

        coze.knowledge.documents.delete(document_ids=["id"])

    def test_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/open_api/knowledge/document/list").mock(
            httpx.Response(
                200,
                json={
                    "data": {
                        "total": 1,
                        "document_infos": [
                            Document.model_validate(
                                {
                                    "document_id": "str",
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
                            ).model_dump()
                        ],
                    }
                },
            )
        )

        res = coze.knowledge.documents.list(dataset_id="id")
        assert res
        assert res.total == 1
