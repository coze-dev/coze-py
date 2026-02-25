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
        **kwargs,
    ) -> List[Document]:
        warnings.warn(
            "The 'coze.knowledge.documents.create' method is deprecated and will be removed in a future version. "
            "Please use 'coze.datasets.documents.create' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        """
        创建知识库文件

        ❌ ❌ 上传方式 通过 Base 64 上传本地文件 上传在线网页 ✅ 调用此 API 向指定的扣子知识库上传文件。 接口说明 通过此 API，你可以向文本或图片知识库中上传文件。 本 API 仅适用于扣子知识库的文件上传操作，不适用于火山知识库上传文件。火山知识库上传文件请参见 火山知识库上传文件 。 上传图片到图片知识库时，可以通过 caption_type 参数设置系统标注或手动标注，如果选择手动标注，还需要调用 更新知识库图片描述 API 手动设置标注。 支持的上传方式如下： 注意事项 每次最多可上传 10 个文件。 必须上传和知识库类型匹配的文件，例如 txt 等文档类型的文件只能上传到文档知识库中，不可上传到表格知识库中。 每个请求只能选择一种上传方式，不支持同时上传在线网页和本地文档。 仅知识库的所有者可以向知识库中上传文件。 ❌ 通过 上传文件 上传 文本知识库 图片知识库 ✅ 格式支持 pdf、txt、doc、docx 类型。 ✅

        :param document_bases: 表格类型一次只能创建一个待创建的文档信息
        """
        url = f"{self._base_url}/open_api/knowledge/document/create"
        headers = {"Agw-Js-Conv": "str"}
        body = {
            "dataset_id": dataset_id,
            "document_bases": [i.model_dump() for i in document_bases],
            "chunk_strategy": chunk_strategy.model_dump() if chunk_strategy else None,
        }
        return self._requester.request(
            "post", url, False, cast=[Document], headers=headers, body=body, data_field="document_infos"
        )

    def update(
        self,
        *,
        document_id: str,
        document_name: Optional[str] = None,
        update_rule: Optional[DocumentUpdateRule] = None,
        **kwargs,
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
            cast=None,
            headers=headers,
            body=body,
        )

    def delete(self, *, document_ids: List[str], **kwargs) -> None:
        warnings.warn(
            "The 'coze.knowledge.documents.delete' method is deprecated and will be removed in a future version. "
            "Please use 'coze.datasets.documents.delete' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        """
        删除知识库文件

        调用此接口删除扣子知识库中的文本、图片、表格等文件，支持批量删除。
        * 仅知识库的所有者可以删除知识库文件。
        * 知识库分为扣子知识库和火山知识库，该 API 仅用于删除扣子知识库中的文件，不支持删除火山知识库中的文件，如果需要删除火山知识库中的文件，请参见[删除火山知识库文件](https://www.volcengine.com/docs/84313/1254608)。
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
            cast=None,
            headers=headers,
            body=body,
        )

    def list(
        self,
        *,
        dataset_id: str,
        page_num: int = 1,
        page_size: int = 10,
        **kwargs,
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
        **kwargs,
    ) -> List[Document]:
        warnings.warn(
            "The 'coze.knowledge.documents.create' method is deprecated and will be removed in a future version. "
            "Please use 'coze.datasets.documents.create' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        """
        创建知识库文件

        调用此 API 向指定的扣子知识库上传文件。 接口说明 通过此 API，你可以向文本或图片知识库中上传文件。 本 API 仅适用于扣子知识库的文件上传操作，不适用于火山知识库上传文件。火山知识库上传文件请参见 火山知识库上传文件 。 上传图片到图片知识库时，可以通过 caption_type 参数设置系统标注或手动标注，如果选择手动标注，还需要调用 更新知识库图片描述 API 手动设置标注。 支持的上传方式如下： 注意事项 每次最多可上传 10 个文件。 必须上传和知识库类型匹配的文件，例如 txt 等文档类型的文件只能上传到文档知识库中，不可上传到表格知识库中。 每个请求只能选择一种上传方式，不支持同时上传在线网页和本地文档。 仅知识库的所有者可以向知识库中上传文件。 文本知识库 上传在线网页 ✅ 上传方式 ✅ 格式支持 pdf、txt、doc、docx 类型。 图片知识库 ❌ ❌ ✅ 通过 Base 64 上传本地文件 ❌ 通过 上传文件 上传

        :param document_bases: 表格类型一次只能创建一个待创建的文档信息
        """
        url = f"{self._base_url}/open_api/knowledge/document/create"
        headers = {"Agw-Js-Conv": "str"}
        body = {
            "dataset_id": dataset_id,
            "document_bases": [i.model_dump() for i in document_bases],
            "chunk_strategy": chunk_strategy.model_dump() if chunk_strategy else None,
        }
        return await self._requester.arequest(
            "post", url, False, cast=[Document], headers=headers, body=body, data_field="document_infos"
        )

    async def update(
        self,
        *,
        document_id: str,
        document_name: Optional[str] = None,
        update_rule: Optional[DocumentUpdateRule] = None,
        **kwargs,
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

    async def delete(self, *, document_ids: List[str], **kwargs) -> None:
        warnings.warn(
            "The 'coze.knowledge.documents.delete' method is deprecated and will be removed in a future version. "
            "Please use 'coze.datasets.documents.delete' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        """
        删除知识库文件

        调用此接口删除扣子知识库中的文本、图片、表格等文件，支持批量删除。
        * 仅知识库的所有者可以删除知识库文件。
        * 知识库分为扣子知识库和火山知识库，该 API 仅用于删除扣子知识库中的文件，不支持删除火山知识库中的文件，如果需要删除火山知识库中的文件，请参见[删除火山知识库文件](https://www.volcengine.com/docs/84313/1254608)。
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
        **kwargs,
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
