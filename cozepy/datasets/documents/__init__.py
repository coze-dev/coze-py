from enum import IntEnum
from typing import List, Optional

from cozepy.model import AsyncNumberPaged, CozeModel, HTTPRequest, ListResponse, NumberPaged, NumberPagedResponse
from cozepy.request import Requester
from cozepy.util import base64_encode_string, remove_url_trailing_slash


class DocumentChunkStrategy(CozeModel):
    # Segmentation setting. Values include:
    # 0: Automatic segmentation and cleaning. Use preset rules for data segmentation and processing.
    # 1: Custom. At this time, you need to specify segmentation rule details through separator, max_tokens,
    # remove_extra_spaces, and remove_urls_emails.
    # 分段设置。取值包括：
    # 0：自动分段与清洗。采用扣子预置规则进行数据分段与处理。
    # 1：自定义。此时需要通过 separator、max_tokens、remove_extra_spaces 和 remove_urls_emails 分段规则细节。
    chunk_type: Optional[int] = None

    # Image knowledge base annotation method:
    # 0: (Default) System automatically annotates description information
    # 1: Manual annotation
    caption_type: Optional[int] = None

    # Maximum segment length, with a range of 100 to 2000.
    # Required when chunk_type=1.
    # 最大分段长度，取值范围为 100~2000。
    # 在 chunk_type=1 时必选。
    max_tokens: Optional[int] = None

    # Whether to automatically filter continuous spaces, line breaks, and tabs. Values include:
    # true: Automatically filter
    # false: (Default) Do not automatically filter<br>Effective when chunk_type=1.
    # 是否自动过滤连续的空格、换行符和制表符。取值包括：
    # true：自动过滤
    # false：（默认）不自动过滤
    # 在 chunk_type=1 时生效。
    remove_extra_spaces: Optional[bool] = None

    # Whether to automatically filter all URLs and email addresses. Values include:
    # true: Automatically filter
    # false: (Default) Do not automatically filter
    # Effective when chunk_type=1.
    # 是否自动过滤所有 URL 和电子邮箱地址。取值包括：
    # true：自动过滤
    # false：（默认）不自动过滤
    # 在 chunk_type=1 时生效。
    remove_urls_emails: Optional[bool] = None

    # Segmentation identifier.
    # Required when chunk_type=1.
    # 分段标识符。
    # 在 chunk_type=1 时必选。
    separator: Optional[str] = None

    @staticmethod
    def build_auto() -> "DocumentChunkStrategy":
        return DocumentChunkStrategy(chunk_type=0)

    @staticmethod
    def build_custom(
        max_tokens: int, separator: str, remove_extra_spaces: bool = False, remove_urls_emails: bool = False
    ) -> "DocumentChunkStrategy":
        return DocumentChunkStrategy(
            chunk_type=1,
            max_tokens=max_tokens,
            remove_extra_spaces=remove_extra_spaces,
            remove_urls_emails=remove_urls_emails,
            separator=separator,
        )


class DocumentFormatType(IntEnum):
    # Document type, such as txt, pdf, online web pages, etc.
    # 文档类型，例如 txt 、pdf 、在线网页等格式均属于文档类型。
    DOCUMENT = 0

    # 表格类型，例如 xls 表格等格式属于表格类型。
    # Spreadsheet type, such as xls spreadsheets, etc.
    SPREADSHEET = 1

    # 照片类型，例如 png 图片等格式属于照片类型。
    # Photo type, such as png images, etc.
    IMAGE = 2


class DocumentSourceType(IntEnum):
    LOCAL_FILE = 0  # Upload local files.
    ONLINE_WEB = 1  # Upload online web pages.
    CUSTOM = 2  # Custom
    THIRD_PARTY = 3  # Third party
    FRONT_CRAWL = 4  # Front-end crawling
    UPLOAD_FILE_ID = 5  # OpenAPI Upload file_id.
    NOTION = 101
    GOOGLE_DRIVE = 102
    FEISHU_WEB = 103
    LARK_WEB = 104


class DocumentStatus(IntEnum):
    # Processing
    # 处理中
    PROCESSING = 0

    # Completed
    # 处理完毕
    COMPLETED = 1

    # Processing failed, it is recommended to re-upload
    # 处理失败，建议重新上传
    FAILED = 9


class DocumentUpdateType(IntEnum):
    # Do not automatically update
    # 不自动更新
    NO_AUTO_UPDATE = 0

    # Automatically update
    # 自动更新
    AUTO_UPDATE = 1


class Document(CozeModel):
    # File ID.
    document_id: str

    # Total number of characters in the document content.
    char_count: int

    # Segmentation rules.
    chunk_strategy: Optional[DocumentChunkStrategy] = None

    # 文件的格式类型。取值包括：
    # 0：文档类型，例如 txt 、pdf 、在线网页等格式均属于文档类型。
    # 1：表格类型，例如 xls 表格等格式属于表格类型。
    # 2：照片类型，例如 png 图片等格式属于照片类型。
    # The type of file format. Values include:
    # 0: Document type, such as txt, pdf, online web pages, etc.
    # 1: Spreadsheet type, such as xls spreadsheets, etc.
    # 2: Photo type, such as png images, etc.
    format_type: DocumentFormatType

    # The number of times the file has been hit in conversations.
    # 被对话命中的次数。
    hit_count: int

    # The name of the file.
    # 文件的名称。
    name: str

    # The size of the file in bytes.
    # 文件的大小，单位为字节。
    size: int

    # The number of slices the file has been divided into.
    # 文件的分段数量。
    slice_count: int

    # The method of uploading the file. Values include:
    # 0: Upload local files.
    # 1: Upload online web pages.
    # 文件的上传方式。取值包括：
    # 0：上传本地文件。
    # 1：上传在线网页。
    source_type: DocumentSourceType

    # The processing status of the file. Values include:
    # 0: Processing
    # 1: Completed
    # 9: Processing failed, it is recommended to re-upload
    # 文件的处理状态。取值包括：
    # 0：处理中
    # 1：处理完毕
    # 9：处理失败，建议重新上传
    status: DocumentStatus

    # The format of the local file, i.e., the file extension, such as "txt". Supported formats include PDF, TXT, DOC,
    # DOCX.
    # 本地文件格式，即文件后缀，例如 txt。格式支持 pdf、txt、doc、docx 类型。
    type: str

    # The frequency of automatic updates for online web pages, in hours.
    # 在线网页自动更新的频率。单位为小时。
    update_interval: int

    # Whether the online web page is automatically updated. Values include:
    # 0: Do not automatically update
    # 1: Automatically update
    # 在线网页是否自动更新。取值包括：
    # 0：不自动更新
    # 1：自动更新
    update_type: DocumentUpdateType

    # The upload time of the file, in the format of a 10-digit Unix timestamp.
    create_time: int

    # The last modified time of the file, in the format of a 10-digit Unix timestamp.
    update_time: int


class DocumentSourceInfo(CozeModel):
    # 本地文件的 Base64 编码。
    # 上传本地文件时必选
    file_base64: Optional[str] = None

    # 本地文件格式，即文件后缀，例如 txt。格式支持 pdf、txt、doc、docx 类型。
    # 上传的文件类型应与知识库类型匹配，例如 txt 文件只能上传到文档类型的知识库中。
    # 上传本地文件时必选
    file_type: Optional[str] = None

    # 网页的 URL 地址。
    # 上传在线网页时必选
    web_url: Optional[str] = None

    source_file_id: Optional[str] = None  # uploaded by `coze.files.upload`

    # 文件的上传方式。支持设置为 1，表示上传在线网页。
    # 上传在线网页时必选
    document_source: Optional[DocumentSourceType] = None

    @staticmethod
    def build_local_file(content: str, file_type: str = "txt") -> "DocumentSourceInfo":
        return DocumentSourceInfo(file_base64=base64_encode_string(content), file_type=file_type)

    @staticmethod
    def build_web_page(url: str) -> "DocumentSourceInfo":
        return DocumentSourceInfo(web_url=url, document_source=DocumentSourceType.ONLINE_WEB)

    @staticmethod
    def build_file_id(file_id: str) -> "DocumentSourceInfo":
        return DocumentSourceInfo(source_file_id=file_id, document_source=DocumentSourceType.UPLOAD_FILE_ID)


class DocumentUpdateRule(CozeModel):
    # 在线网页是否自动更新。取值包括：
    # 0：不自动更新
    # 1：自动更新
    update_type: DocumentUpdateType

    # 在线网页自动更新的频率。单位为小时，最小值为 24。
    update_interval: int

    @staticmethod
    def build_no_auto_update() -> "DocumentUpdateRule":
        return DocumentUpdateRule(update_type=DocumentUpdateType.NO_AUTO_UPDATE, update_interval=24)

    @staticmethod
    def build_auto_update(interval: int) -> "DocumentUpdateRule":
        return DocumentUpdateRule(update_type=DocumentUpdateType.AUTO_UPDATE, update_interval=interval)


class DocumentBase(CozeModel):
    # 文件名称。
    name: str

    # 文件的元数据信息。详细信息可参考 DocumentSourceInfo object。
    source_info: DocumentSourceInfo

    # 在线网页的更新策略。默认不自动更新。
    update_rule: Optional[DocumentUpdateRule] = None


class UpdateDocumentRes(CozeModel):
    pass


class DeleteDocumentRes(CozeModel):
    pass


class _PrivateListDocumentsData(CozeModel, NumberPagedResponse[Document]):
    document_infos: List[Document]
    total: int

    def get_total(self) -> Optional[int]:
        return self.total

    def get_has_more(self) -> Optional[bool]:
        return None

    def get_items(self) -> List[Document]:
        return self.document_infos


class DatasetsDocumentsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(
        self,
        *,
        dataset_id: str,
        document_bases: List[DocumentBase],
        chunk_strategy: Optional[DocumentChunkStrategy] = None,
        format_type: Optional[DocumentFormatType] = DocumentFormatType.DOCUMENT,
    ) -> ListResponse[Document]:
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
            "format_type": format_type,
        }
        return self._requester.request(
            "post", url, False, ListResponse[Document], headers=headers, body=body, data_field="document_infos"
        )

    def update(
        self,
        *,
        document_id: str,
        document_name: Optional[str] = None,
        update_rule: Optional[DocumentUpdateRule] = None,
    ) -> UpdateDocumentRes:
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
            cast=UpdateDocumentRes,
            headers=headers,
            body=body,
        )

    def delete(
        self,
        *,
        document_ids: List[str],
    ) -> DeleteDocumentRes:
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
            cast=DeleteDocumentRes,
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


class AsyncDatasetsDocumentsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def create(
        self,
        *,
        dataset_id: str,
        document_bases: List[DocumentBase],
        chunk_strategy: Optional[DocumentChunkStrategy] = None,
    ) -> ListResponse[Document]:
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
            "post", url, False, ListResponse[Document], headers=headers, body=body, data_field="document_infos"
        )

    async def update(
        self,
        *,
        document_id: str,
        document_name: Optional[str] = None,
        update_rule: Optional[DocumentUpdateRule] = None,
    ) -> UpdateDocumentRes:
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
            cast=UpdateDocumentRes,
            headers=headers,
            body=body,
        )

    async def delete(
        self,
        *,
        document_ids: List[str],
    ) -> DeleteDocumentRes:
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
            cast=DeleteDocumentRes,
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
