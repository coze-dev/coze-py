from enum import IntEnum

from cozepy import NumberPaged
from cozepy.auth import Auth
from cozepy.model import CozeModel
from cozepy.request import Requester


class DocumentChunkStrategy(CozeModel):
    # Segmentation setting. Values include:
    # 0: Automatic segmentation and cleaning. Use preset rules for data segmentation and processing.
    # 1: Custom. At this time, you need to specify segmentation rule details through separator, max_tokens,
    # remove_extra_spaces, and remove_urls_emails.
    chunk_type: int

    # Maximum segment length, with a range of 100 to 2000.
    # Required when chunk_type=1.
    max_tokens: int

    # Whether to automatically filter continuous spaces, line breaks, and tabs. Values include:
    # true: Automatically filter
    # false: (Default) Do not automatically filter<br>Effective when chunk_type=1.
    remove_extra_spaces: bool

    # Whether to automatically filter all URLs and email addresses. Values include:
    # true: Automatically filter
    # false: (Default) Do not automatically filter
    # Effective when chunk_type=1.
    remove_urls_emails: bool

    # Segmentation identifier.
    # Required when chunk_type=1.
    separator: str


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
    # Upload local files.
    # 上传本地文件。
    LOCAL_FILE = 0

    # Upload online web pages.
    # 上传在线网页。
    ONLINE_WEB = 1


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
    # The ID of the file.
    # 文件的 ID。
    document_id: int  # TODO: fixme

    # The total character count of the file content.
    # 文件内容的总字符数量。
    char_count: int

    # The chunking rules. For detailed instructions, refer to the ChunkStrategy object.
    # 分段规则。详细说明可参考 chunk_strategy object。
    chunk_strategy: DocumentChunkStrategy

    # The upload time of the file, in the format of a 10-digit Unix timestamp.
    # 文件的上传时间，格式为 10 位的 Unixtime 时间戳。
    create_time: int

    # The last modified time of the file, in the format of a 10-digit Unix timestamp.
    # 文件的最近一次修改时间，格式为 10 位的 Unixtime 时间戳。
    update_time: int

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


class DocumentsClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester

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
        params = {
            "dataset_id": dataset_id,
            "page": page_num,
            "size": page_size,
        }
        res = self._requester.request("get", url, self._PrivateListDocumentsV1Data, params=params)
        return NumberPaged(
            items=res.document_infos,
            page_num=page_num,
            page_size=page_size,
            total=res.total,
        )

    class _PrivateListDocumentsV1Data(CozeModel):
        document_infos: list[Document]
        total: int
