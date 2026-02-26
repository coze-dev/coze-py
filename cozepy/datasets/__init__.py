from enum import IntEnum
from typing import TYPE_CHECKING, List, Optional

from cozepy.datasets.documents import DocumentChunkStrategy, DocumentFormatType, DocumentStatus, DocumentUpdateType
from cozepy.model import AsyncNumberPaged, CozeModel, HTTPRequest, ListResponse, NumberPaged, NumberPagedResponse
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash

if TYPE_CHECKING:
    from cozepy.datasets.documents import AsyncDatasetsDocumentsClient, DatasetsDocumentsClient
    from cozepy.datasets.images import AsyncDatasetsImagesClient, DatasetsImagesClient


class CreateDatasetResp(CozeModel):
    dataset_id: str


class DatasetStatus(IntEnum):
    ENABLED = 1
    DISABLED = 3


class Dataset(CozeModel):
    dataset_id: str  # The ID of the dataset
    # 数据集名称
    name: str
    description: str  # The description of the dataset
    # 空间ID
    space_id: str
    status: DatasetStatus  # The status of the dataset, 1: enable, 3: disable
    format_type: DocumentFormatType  # The format type of the dataset, 0: text, 1: table, 2: image
    # 是否可以编辑
    can_edit: bool = False
    icon_url: str = ""  # The icon URL of the dataset
    # 文档数量
    doc_count: int = 0
    # 文件列表
    file_list: List[str] = []
    # 命中次数
    hit_count: int = 0
    # 使用Bot数
    bot_used_count: int = 0
    # 分段数量
    slice_count: int = 0
    # 所有文件大小
    all_file_size: int = 0
    chunk_strategy: Optional[DocumentChunkStrategy] = None  # The chunk strategy of the dataset
    # 处理失败的文件
    failed_file_list: List[str] = []
    # 处理中的文件名称列表，兼容老逻辑
    processing_file_list: List[str] = []
    # 处理中的文件ID列表
    processing_file_id_list: List[str] = []
    avatar_url: str = ""  # The avatar URL of the dataset creator
    # 创建者ID
    creator_id: str = ""
    creator_name: str = ""  # The name of the dataset creator
    # 创建时间，秒级时间戳
    create_time: int = 0
    # 更新时间，秒级时间戳
    update_time: int = 0


class _PrivateListDatasetsData(CozeModel, NumberPagedResponse[Dataset]):
    total_count: int
    dataset_list: List[Dataset]

    def get_total(self) -> Optional[int]:
        return self.total_count

    def get_has_more(self) -> Optional[bool]:
        return None

    def get_items(self) -> List[Dataset]:
        return self.dataset_list


class DocumentProgress(CozeModel):
    document_id: str = ""  # File ID.
    url: str = ""  # File address.
    size: int = 0  # The size of the file, in bytes.
    type: str = (
        ""  # Local file format, i.e., the file extension, such as txt. Format supports pdf, txt, doc, docx types.
    )
    status: DocumentStatus  # File processing status. Values include: 0: In processing, 1: Processing completed, 9: Processing failed, recommend re-uploading
    progress: int = 0  # File upload progress. Unit is percentage.
    update_type: DocumentUpdateType  # Will the webpage automatically update online. Values include:
    document_name: str = ""  # File name.
    remaining_time: int = 0  # Estimated remaining time, in seconds.
    # 状态的详细描述；如果切片失败，返回失败信息
    status_descript: str = ""
    # 更新间隔
    update_interval: int = 0


class UpdateDatasetRes(CozeModel):
    pass


class DeleteDatasetRes(CozeModel):
    pass


class DatasetsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._documents: Optional[DatasetsDocumentsClient] = None
        self._images: Optional[DatasetsImagesClient] = None

    @property
    def documents(self) -> "DatasetsDocumentsClient":
        if not self._documents:
            from .documents import DatasetsDocumentsClient

            self._documents = DatasetsDocumentsClient(base_url=self._base_url, requester=self._requester)
        return self._documents

    @property
    def images(self) -> "DatasetsImagesClient":
        if not self._images:
            from .images import DatasetsImagesClient

            self._images = DatasetsImagesClient(base_url=self._base_url, requester=self._requester)
        return self._images

    def create(
        self,
        *,
        name: str,
        space_id: str,
        format_type: DocumentFormatType,
        description: Optional[str] = None,
        icon_file_id: Optional[str] = None,
        **kwargs,
    ) -> CreateDatasetResp:
        """
        Create Dataset

        docs en: https://www.coze.com/docs/developer_guides/create_dataset
        docs zh: https://www.coze.cn/docs/developer_guides/create_dataset

        :param name: The name of the dataset
        :param space_id: The ID of the space that the dataset belongs to
        :param format_type: The format type of the dataset, 0: text, 2: image
        :param description: The description of the dataset
        :param icon_file_id: The ID of the icon file, uploaded by `coze.files.upload`
        """
        url = f"{self._base_url}/v1/datasets"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "name": name,
            "space_id": space_id,
            "format_type": format_type,
            "description": description,
            "file_id": icon_file_id,
        }
        return self._requester.request("post", url, False, cast=CreateDatasetResp, headers=headers, body=body)

    def update(
        self,
        *,
        dataset_id: str,
        name: str,
        description: Optional[str] = None,
        icon_file_id: Optional[str] = None,
        **kwargs,
    ) -> UpdateDatasetRes:
        """
        修改知识库信息

        调用此接口修改扣子知识库信息。
        * 此接口会全量刷新知识库的 name、file_id 和 description 配置，如果未设置这些参数，参数将恢复默认配置。
        * 知识库分为扣子知识库和火山知识库，该 API 仅用于修改扣子知识库，不支持修改火山知识库，如果需要修改火山知识库的信息，请参见[修改火山知识库信息 API 文档](https://whttps://www.volcengine.com/docs/84313/1254592)。
        * 仅支持修改本人为所有者的知识库信息，包括知识库名称、图标、描述等信息。
        * 如需修改知识库图标，需要先调用 API [上传文件](https://www.coze.cn/docs/developer_guides/upload_files)，将图片文件上传至扣子平台。

        :param dataset_id: 知识库 ID。 在扣子平台中打开指定知识库页面，页面 URL 中 `knowledge` 参数后的数字就是知识库 ID。例如 `https://www.coze.cn/space/736142423532160****/knowledge/738509371792341****`，知识库 ID 为 `738509371792341****`。
        """
        url = f"{self._base_url}/v1/datasets/{dataset_id}"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "name": name,
            "description": description,
            "file_id": icon_file_id,
        }
        return self._requester.request("put", url, False, cast=UpdateDatasetRes, headers=headers, body=body)

    def delete(self, *, dataset_id: str, **kwargs) -> DeleteDatasetRes:
        """
        Delete Dataset
        The workspace administrator can delete all knowledge bases in the team, while other members can only delete knowledge bases they own.
        When deleting a knowledge base, all files uploaded to the knowledge base will be deleted simultaneously, and any agents bound to this knowledge base will be automatically unbound.

        docs en: https://www.coze.com/docs/developer_guides/delete_dataset
        docs zh: https://www.coze.cn/docs/developer_guides/delete_dataset

        :param dataset_id: The ID of the dataset
        """
        url = f"{self._base_url}/v1/datasets/{dataset_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("delete", url, False, cast=DeleteDatasetRes, headers=headers)

    def list(
        self,
        *,
        space_id: str,
        name: Optional[str] = None,
        format_type: Optional[DocumentFormatType] = None,
        page_size: int = 10,
        page_num: int = 1,
        **kwargs,
    ) -> NumberPaged[Dataset]:
        """
        List Datasets

        docs en: https://www.coze.com/docs/developer_guides/list_dataset
        docs zh: https://www.coze.cn/docs/developer_guides/list_dataset

        :param space_id: The ID of the space that the dataset belongs to
        :param name: The name of the dataset, supports fuzzy search
        :param format_type: The format type of the dataset, 0: text, 1: table, 2: image
        :param page_num: The page number. The minimum value is 1, and the default is 1.
        :param page_size: The page size. The value range is 1~300, and the default is 10.
        """
        url = f"{self._base_url}/v1/datasets"
        headers: Optional[dict] = kwargs.get("headers")

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                headers=headers,
                params={
                    "space_id": space_id,
                    "name": name,
                    "format_type": format_type,
                    "page_size": i_page_size,
                    "page_num": i_page_num,
                },
                cast=_PrivateListDatasetsData,
                stream=False,
            )

        return NumberPaged(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )

    def process(self, *, dataset_id: str, document_ids: List[str], **kwargs) -> ListResponse[DocumentProgress]:
        """
        查看知识库文件上传进度

        调用此接口获取扣子知识库文件的上传进度。
        此接口支持查看所有类型知识库文件的上传进度，例如文本、图片、表格。
        支持批量查看多个文件的进度，多个文件必须位于同一个知识库中。
        该 API 仅支持查看扣子知识库中的文件上传进度，不支持查看火山知识库中的文件上传进度。

        :param dataset_id: 扣子知识库 ID。不能填写火山知识库 ID。 在扣子编程中打开指定扣子知识库页面，页面 URL 中 `knowledge` 参数后的数字就是扣子知识库 ID。例如 `https://www.coze.cn/space/736142423532160****/knowledge/738509371792341****`，扣子知识库 ID 为 `738509371792341****`。
        """
        url = f"{self._base_url}/v1/datasets/{dataset_id}/process"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "document_ids": document_ids,
        }
        return self._requester.request(
            "post", url, False, cast=ListResponse[DocumentProgress], headers=headers, body=body, data_field="data.data"
        )


class AsyncDatasetsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._documents: Optional[AsyncDatasetsDocumentsClient] = None
        self._images: Optional[AsyncDatasetsImagesClient] = None

    @property
    def documents(self) -> "AsyncDatasetsDocumentsClient":
        if not self._documents:
            from .documents import AsyncDatasetsDocumentsClient

            self._documents = AsyncDatasetsDocumentsClient(base_url=self._base_url, requester=self._requester)
        return self._documents

    @property
    def images(self) -> "AsyncDatasetsImagesClient":
        if not self._images:
            from .images import AsyncDatasetsImagesClient

            self._images = AsyncDatasetsImagesClient(base_url=self._base_url, requester=self._requester)
        return self._images

    async def create(
        self,
        *,
        name: str,
        space_id: str,
        format_type: DocumentFormatType,
        description: Optional[str] = None,
        icon_file_id: Optional[str] = None,
        **kwargs,
    ) -> CreateDatasetResp:
        """
        Create Dataset

        :param name: The name of the dataset
        :param space_id: The ID of the space that the dataset belongs to
        :param format_type: The format type of the dataset, 0: text, 2: image
        :param description: The description of the dataset
        :param icon_file_id: The ID of the icon file, uploaded by `coze.files.upload`
        """
        url = f"{self._base_url}/v1/datasets"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "name": name,
            "space_id": space_id,
            "format_type": format_type,
            "description": description,
            "file_id": icon_file_id,
        }
        return await self._requester.arequest("post", url, False, cast=CreateDatasetResp, headers=headers, body=body)

    async def update(
        self,
        *,
        dataset_id: str,
        name: str,
        description: Optional[str] = None,
        icon_file_id: Optional[str] = None,
        **kwargs,
    ) -> UpdateDatasetRes:
        """
        修改知识库信息

        调用此接口修改扣子知识库信息。
        * 此接口会全量刷新知识库的 name、file_id 和 description 配置，如果未设置这些参数，参数将恢复默认配置。
        * 知识库分为扣子知识库和火山知识库，该 API 仅用于修改扣子知识库，不支持修改火山知识库，如果需要修改火山知识库的信息，请参见[修改火山知识库信息 API 文档](https://whttps://www.volcengine.com/docs/84313/1254592)。
        * 仅支持修改本人为所有者的知识库信息，包括知识库名称、图标、描述等信息。
        * 如需修改知识库图标，需要先调用 API [上传文件](https://www.coze.cn/docs/developer_guides/upload_files)，将图片文件上传至扣子平台。

        :param dataset_id: 知识库 ID。 在扣子平台中打开指定知识库页面，页面 URL 中 `knowledge` 参数后的数字就是知识库 ID。例如 `https://www.coze.cn/space/736142423532160****/knowledge/738509371792341****`，知识库 ID 为 `738509371792341****`。
        """
        url = f"{self._base_url}/v1/datasets/{dataset_id}"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "name": name,
            "description": description,
            "file_id": icon_file_id,
        }
        return await self._requester.arequest("put", url, False, cast=UpdateDatasetRes, headers=headers, body=body)

    async def delete(self, *, dataset_id: str, **kwargs) -> DeleteDatasetRes:
        """
        Delete Dataset
        The workspace administrator can delete all knowledge bases in the team, while other members can only delete knowledge bases they own.
        When deleting a knowledge base, all files uploaded to the knowledge base will be deleted simultaneously, and any agents bound to this knowledge base will be automatically unbound.

        docs en: https://www.coze.com/docs/developer_guides/delete_dataset
        docs zh: https://www.coze.cn/docs/developer_guides/delete_dataset

        :param dataset_id: The ID of the dataset
        """
        url = f"{self._base_url}/v1/datasets/{dataset_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest("delete", url, False, cast=DeleteDatasetRes, headers=headers)

    async def list(
        self,
        *,
        space_id: str,
        name: Optional[str] = None,
        format_type: Optional[DocumentFormatType] = None,
        page_size: int = 10,
        page_num: int = 1,
        **kwargs,
    ) -> AsyncNumberPaged[Dataset]:
        """
        List Datasets

        docs en: https://www.coze.com/docs/developer_guides/list_dataset
        docs zh: https://www.coze.cn/docs/developer_guides/list_dataset

        :param space_id: The ID of the space that the dataset belongs to
        :param name: The name of the dataset, supports fuzzy search
        :param format_type: The format type of the dataset, 0: text, 1: table, 2: image
        :param page_num: The page number. The minimum value is 1, and the default is 1.
        :param page_size: The page size. The value range is 1~300, and the default is 10.
        """
        url = f"{self._base_url}/v1/datasets"
        headers: Optional[dict] = kwargs.get("headers")

        async def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "GET",
                url,
                headers=headers,
                params={
                    "space_id": space_id,
                    "name": name,
                    "format_type": format_type,
                    "page_size": i_page_size,
                    "page_num": i_page_num,
                },
                cast=_PrivateListDatasetsData,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )

    async def process(self, *, dataset_id: str, document_ids: List[str], **kwargs) -> ListResponse[DocumentProgress]:
        """
        查看知识库文件上传进度

        调用此接口获取扣子知识库文件的上传进度。
        此接口支持查看所有类型知识库文件的上传进度，例如文本、图片、表格。
        支持批量查看多个文件的进度，多个文件必须位于同一个知识库中。
        该 API 仅支持查看扣子知识库中的文件上传进度，不支持查看火山知识库中的文件上传进度。

        :param dataset_id: 扣子知识库 ID。不能填写火山知识库 ID。 在扣子编程中打开指定扣子知识库页面，页面 URL 中 `knowledge` 参数后的数字就是扣子知识库 ID。例如 `https://www.coze.cn/space/736142423532160****/knowledge/738509371792341****`，扣子知识库 ID 为 `738509371792341****`。
        """
        url = f"{self._base_url}/v1/datasets/{dataset_id}/process"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "document_ids": document_ids,
        }
        return await self._requester.arequest(
            "post", url, False, cast=ListResponse[DocumentProgress], headers=headers, body=body, data_field="data.data"
        )
