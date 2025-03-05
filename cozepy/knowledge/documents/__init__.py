import warnings
from typing import List, Optional

from cozepy.datasets.documents import (
    Document,
    DocumentBase,
    DocumentChunkStrategy,
    DocumentUpdateRule,
)
from cozepy.model import AsyncNumberPaged, CozeModel, HTTPRequest, NumberPaged, NumberPagedResponse
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


class _PrivateListDocumentsData(CozeModel, NumberPagedResponse[Document]):
    document_infos: List[Document]
    total: int

    def get_total(self) -> Optional[int]:
        return self.total

    def get_has_more(self) -> Optional[bool]:
        return None

    def get_items(self) -> List[Document]:
        return self.document_infos


class DocumentsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        warnings.warn(
            "The 'coze.knowledge.documents' module is deprecated and will be removed in a future version. "
            "Please use 'coze.datasets' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(
        self,
        *,
        dataset_id: str,
        document_bases: List[DocumentBase],
        chunk_strategy: Optional[DocumentChunkStrategy] = None,
    ) -> List[Document]:
        warnings.warn(
            "The 'coze.knowledge.documents.create' method is deprecated and will be removed in a future version. "
            "Please use 'coze.datasets.documents.create' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        """
        Upload files to the specific knowledge.

        docs en: https://www.coze.com/docs/developer_guides/create_knowledge_files
        docs zh: https://www.coze.cn/docs/developer_guides/create_knowledge_files

        :param dataset_id: The ID of the knowledge base.
        :param document_bases: The metadata information of the files awaiting upload. The array has a maximum length of
        10, meaning up to 10 files can be uploaded at a time. For detailed instructions, refer to the DocumentBase
        object.
        :param chunk_strategy: Chunk strategy. These rules must be set only when uploading a file to a new knowledge
        for the first time. For subsequent file uploads to this knowledge, it is not necessary to pass these rules; the
        default is to continue using the initial settings, and modifications are not supported.
        For detailed instructions, refer to the ChunkStrategy object.
        :return: list of Document
        """
        url = f"{self._base_url}/open_api/knowledge/document/create"
        headers = {"Agw-Js-Conv": "str"}
        body = {
            "dataset_id": dataset_id,
            "document_bases": [i.model_dump() for i in document_bases],
            "chunk_strategy": chunk_strategy.model_dump() if chunk_strategy else None,
        }
        return self._requester.request(
            "post", url, False, [Document], headers=headers, body=body, data_field="document_infos"
        )

    def update(
        self,
        *,
        document_id: str,
        document_name: Optional[str] = None,
        update_rule: Optional[DocumentUpdateRule] = None,
    ) -> None:
        warnings.warn(
            "The 'coze.knowledge.documents.update' method is deprecated and will be removed in a future version. "
            "Please use 'coze.datasets.documents.update' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        """
        Modify the knowledge base file name and update strategy.

        docs en: https://www.coze.com/docs/developer_guides/modify_knowledge_files
        docs zh: https://www.coze.cn/docs/developer_guides/modify_knowledge_files

        :param document_id: The ID of the knowledge base file.
        :param document_name: The new name of the knowledge base file.
        :param update_rule: The update strategy for online web pages. Defaults to no automatic updates.
        For detailed information, refer to the UpdateRule object.
        :return: None
        """
        url = f"{self._base_url}/open_api/knowledge/document/update"
        headers = {"Agw-Js-Conv": "str"}
        body = {
            "document_id": document_id,
            "document_name": document_name,
            "update_rule": update_rule,
        }
        return self._requester.request(
            "post",
            url,
            False,
            None,
            headers=headers,
            body=body,
        )

    def delete(
        self,
        *,
        document_ids: List[str],
    ) -> None:
        warnings.warn(
            "The 'coze.knowledge.documents.delete' method is deprecated and will be removed in a future version. "
            "Please use 'coze.datasets.documents.delete' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        """
        Delete text, images, sheets, and other files in the knowledge base, supporting batch deletion.

        docs en: https://www.coze.com/docs/developer_guides/delete_knowledge_files
        docs zh: https://www.coze.cn/docs/developer_guides/delete_knowledge_files

        :param document_ids: The list of knowledge base files to be deleted. The maximum length of the array is 100,
        meaning a maximum of 100 files can be deleted at one time.
        :return: None
        """
        url = f"{self._base_url}/open_api/knowledge/document/delete"
        headers = {"Agw-Js-Conv": "str"}
        body = {
            "document_ids": document_ids,
        }
        return self._requester.request(
            "post",
            url,
            False,
            None,
            headers=headers,
            body=body,
        )

    def list(
        self,
        *,
        dataset_id: str,
        page_num: int = 1,
        page_size: int = 10,
    ) -> NumberPaged[Document]:
        warnings.warn(
            "The 'coze.knowledge.documents.list' method is deprecated and will be removed in a future version. "
            "Please use 'coze.datasets.documents.list' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        """
        View the file list of a specified knowledge base, which includes lists of documents, spreadsheets, or images.

        docs en: https://www.coze.com/docs/developer_guides/list_knowledge_files
        docs zh: https://www.coze.cn/docs/developer_guides/list_knowledge_files


        :param dataset_id: The ID of the knowledge base.
        :param page_num: The page number for paginated queries. Default is 1, meaning the data return starts from the
        first page.
        :param page_size: The size of pagination. Default is 10, meaning that 10 data entries are returned per page.
        :return: list of Document
        """
        url = f"{self._base_url}/open_api/knowledge/document/list"
        headers = {"Agw-Js-Conv": "str"}

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "POST",
                url,
                headers=headers,
                json={
                    "dataset_id": dataset_id,
                    "page": i_page_num,
                    "size": i_page_size,
                },
                cast=_PrivateListDocumentsData,
                stream=False,
            )

        return NumberPaged(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )


class AsyncDocumentsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        warnings.warn(
            "The 'coze.knowledge.documents' module is deprecated and will be removed in a future version. "
            "Please use 'coze.datasets.documents' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def create(
        self,
        *,
        dataset_id: str,
        document_bases: List[DocumentBase],
        chunk_strategy: Optional[DocumentChunkStrategy] = None,
    ) -> List[Document]:
        warnings.warn(
            "The 'coze.knowledge.documents.create' method is deprecated and will be removed in a future version. "
            "Please use 'coze.datasets.documents.create' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        """
        Upload files to the specific knowledge.

        docs en: https://www.coze.com/docs/developer_guides/create_knowledge_files
        docs zh: https://www.coze.cn/docs/developer_guides/create_knowledge_files

        :param dataset_id: The ID of the knowledge base.
        :param document_bases: The metadata information of the files awaiting upload. The array has a maximum length of
        10, meaning up to 10 files can be uploaded at a time. For detailed instructions, refer to the DocumentBase
        object.
        :param chunk_strategy: Chunk strategy. These rules must be set only when uploading a file to a new knowledge
        for the first time. For subsequent file uploads to this knowledge, it is not necessary to pass these rules; the
        default is to continue using the initial settings, and modifications are not supported.
        For detailed instructions, refer to the ChunkStrategy object.
        :return: list of Document
        """
        url = f"{self._base_url}/open_api/knowledge/document/create"
        headers = {"Agw-Js-Conv": "str"}
        body = {
            "dataset_id": dataset_id,
            "document_bases": [i.model_dump() for i in document_bases],
            "chunk_strategy": chunk_strategy.model_dump() if chunk_strategy else None,
        }
        return await self._requester.arequest(
            "post", url, False, [Document], headers=headers, body=body, data_field="document_infos"
        )

    async def update(
        self,
        *,
        document_id: str,
        document_name: Optional[str] = None,
        update_rule: Optional[DocumentUpdateRule] = None,
    ) -> None:
        warnings.warn(
            "The 'coze.knowledge.documents.update' method is deprecated and will be removed in a future version. "
            "Please use 'coze.datasets.documents.update' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        """
        Modify the knowledge base file name and update strategy.

        docs en: https://www.coze.com/docs/developer_guides/modify_knowledge_files
        docs zh: https://www.coze.cn/docs/developer_guides/modify_knowledge_files

        :param document_id: The ID of the knowledge base file.
        :param document_name: The new name of the knowledge base file.
        :param update_rule: The update strategy for online web pages. Defaults to no automatic updates.
        For detailed information, refer to the UpdateRule object.
        :return: None
        """
        url = f"{self._base_url}/open_api/knowledge/document/update"
        headers = {"Agw-Js-Conv": "str"}
        body = {
            "document_id": document_id,
            "document_name": document_name,
            "update_rule": update_rule,
        }
        return await self._requester.arequest(
            "post",
            url,
            False,
            cast=None,
            headers=headers,
            body=body,
        )

    async def delete(
        self,
        *,
        document_ids: List[str],
    ) -> None:
        warnings.warn(
            "The 'coze.knowledge.documents.delete' method is deprecated and will be removed in a future version. "
            "Please use 'coze.datasets.documents.delete' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        """
        Delete text, images, sheets, and other files in the knowledge base, supporting batch deletion.

        docs en: https://www.coze.com/docs/developer_guides/delete_knowledge_files
        docs zh: https://www.coze.cn/docs/developer_guides/delete_knowledge_files

        :param document_ids: The list of knowledge base files to be deleted. The maximum length of the array is 100,
        meaning a maximum of 100 files can be deleted at one time.
        :return: None
        """
        url = f"{self._base_url}/open_api/knowledge/document/delete"
        headers = {"Agw-Js-Conv": "str"}
        body = {
            "document_ids": document_ids,
        }
        return await self._requester.arequest(
            "post",
            url,
            False,
            cast=None,
            headers=headers,
            body=body,
        )

    async def list(
        self,
        *,
        dataset_id: str,
        page_num: int = 1,
        page_size: int = 10,
    ) -> AsyncNumberPaged[Document]:
        warnings.warn(
            "The 'coze.knowledge.documents.list' method is deprecated and will be removed in a future version. "
            "Please use 'coze.datasets.documents.list' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        """
        View the file list of a specified knowledge base, which includes lists of documents, spreadsheets, or images.

        docs en: https://www.coze.com/docs/developer_guides/list_knowledge_files
        docs zh: https://www.coze.cn/docs/developer_guides/list_knowledge_files


        :param dataset_id: The ID of the knowledge base.
        :param page_num: The page number for paginated queries. Default is 1, meaning the data return starts from the
        first page.
        :param page_size: The size of pagination. Default is 10, meaning that 10 data entries are returned per page.
        :return: list of Document
        """
        url = f"{self._base_url}/open_api/knowledge/document/list"
        headers = {"Agw-Js-Conv": "str"}

        async def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "POST",
                url,
                headers=headers,
                json={
                    "dataset_id": dataset_id,
                    "page": i_page_num,
                    "size": i_page_size,
                },
                cast=_PrivateListDocumentsData,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )
