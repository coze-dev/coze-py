from enum import IntEnum
from typing import TYPE_CHECKING, List, Optional

from cozepy.auth import Auth
from cozepy.datasets.documents import DocumentChunkStrategy
from cozepy.model import AsyncNumberPaged, CozeModel, HTTPRequest, NumberPaged, NumberPagedResponse
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash

if TYPE_CHECKING:
    from .documents import AsyncDatasetsDocumentsClient, DatasetsDocumentsClient


class CreateDatasetRes(CozeModel):
    dataset_id: str


class DatasetFormatType(IntEnum):
    TEXT = 0
    TABLE = 1
    IMAGE = 2


class DatasetStatus(IntEnum):
    ENABLED = 1
    DISABLED = 3


class Dataset(CozeModel):
    dataset_id: str  # The ID of the dataset
    name: str  # The name of the dataset
    description: str  # The description of the dataset
    space_id: str  # The ID of the space that the dataset belongs to
    status: DatasetStatus  # The status of the dataset, 1: enable, 3: disable
    format_type: DatasetFormatType  # The format type of the dataset, 0: text, 1: table, 2: image
    can_edit: bool = False  # Whether the dataset can be edited
    icon_url: str = ""  # The icon URL of the dataset
    doc_count: int = 0  # The count of the documents in the dataset
    file_list: List[str] = []  # The list of files in the dataset
    hit_count: int = 0  # The count of the hits in the dataset
    bot_used_count: int = 0  # The count of the bots used in the dataset
    slice_count: int = 0  # The count of the segments in the dataset
    all_file_size: int = 0  # The total size of all files in the dataset
    chunk_strategy: Optional[DocumentChunkStrategy] = None  # The chunk strategy of the dataset
    failed_file_list: List[str] = []  # The list of files that failed to be uploaded in the dataset
    processing_file_list: List[str] = []  # The list of files that are being processed in the dataset
    processing_file_id_list: List[str] = []  # The list of file IDs that are being processed in the dataset
    avatar_url: str = ""  # The avatar URL of the dataset creator
    creator_id: str = ""  # The ID of the dataset creator
    creator_name: str = ""  # The name of the dataset creator
    create_time: int = 0  # The creation second-level timestamp of the dataset
    update_time: int = 0  # The update second-level timestamp of the dataset


class _PrivateListDatasetsData(CozeModel, NumberPagedResponse[Dataset]):
    total_count: int
    dataset_list: List[Dataset]

    def get_total(self) -> Optional[int]:
        return self.total_count

    def get_has_more(self) -> Optional[bool]:
        return None

    def get_items(self) -> List[Dataset]:
        return self.dataset_list


class DatasetsClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._auth = auth
        self._requester = requester
        self._documents: Optional[DatasetsDocumentsClient] = None

    @property
    def documents(self) -> "DatasetsDocumentsClient":
        if self._documents is None:
            from .documents import DatasetsDocumentsClient

            self._documents = DatasetsDocumentsClient(
                base_url=self._base_url, auth=self._auth, requester=self._requester
            )
        return self._documents

    def create(
        self,
        *,
        name: str,
        space_id: str,
        format_type: DatasetFormatType,
        description: Optional[str] = None,
        icon_file_id: Optional[str] = None,
    ) -> CreateDatasetRes:
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
        body = {
            "name": name,
            "space_id": space_id,
            "format_type": format_type,
            "description": description,
            "file_id": icon_file_id,
        }
        return self._requester.request(
            "post",
            url,
            False,
            CreateDatasetRes,
            body=body,
        )

    def list(
        self,
        *,
        space_id: str,
        name: Optional[str] = None,
        format_type: Optional[DatasetFormatType] = None,
        page_num: int = 1,
        page_size: int = 10,
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
                is_async=False,
                stream=False,
            )

        return NumberPaged(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )

    def update(
        self,
        *,
        dataset_id: str,
        name: str,
        description: Optional[str] = None,
        icon_file_id: Optional[str] = None,
    ) -> CreateDatasetRes:
        """
        Update Dataset
        This API will fully refresh the knowledge base's name, file_id, and description settings. If these parameters are not set, they will revert to default settings.

        docs en: https://www.coze.com/docs/developer_guides/update_dataset
        docs zh: https://www.coze.cn/docs/developer_guides/update_dataset

        :param name: The name of the dataset
        :param description: The description of the dataset
        :param icon_file_id: The ID of the icon file, uploaded by `coze.files.upload`
        """
        url = f"{self._base_url}/v1/datasets/{dataset_id}"
        body = {
            "name": name,
            "description": description,
            "file_id": icon_file_id,
        }
        return self._requester.request(
            "put",
            url,
            False,
            cast=None,
            body=body,
        )


class AsyncDatasetsClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._auth = auth
        self._requester = requester
        self._documents: Optional[AsyncDatasetsDocumentsClient] = None

    async def create(
        self,
        *,
        name: str,
        space_id: str,
        format_type: DatasetFormatType,
        description: Optional[str] = None,
        icon_file_id: Optional[str] = None,
    ) -> CreateDatasetRes:
        """
        Create Dataset

        :param name: The name of the dataset
        :param space_id: The ID of the space that the dataset belongs to
        :param format_type: The format type of the dataset, 0: text, 2: image
        :param description: The description of the dataset
        :param icon_file_id: The ID of the icon file, uploaded by `coze.files.upload`
        """
        url = f"{self._base_url}/v1/datasets"
        body = {
            "name": name,
            "space_id": space_id,
            "format_type": format_type,
            "description": description,
            "file_id": icon_file_id,
        }
        return await self._requester.arequest(
            "post",
            url,
            False,
            CreateDatasetRes,
            body=body,
        )

    async def list(
        self,
        *,
        space_id: str,
        name: Optional[str] = None,
        format_type: Optional[DatasetFormatType] = None,
        page_num: int = 1,
        page_size: int = 10,
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
                is_async=False,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )

    @property
    def documents(self) -> "AsyncDatasetsDocumentsClient":
        if self._documents is None:
            from .documents import AsyncDatasetsDocumentsClient

            self._documents = AsyncDatasetsDocumentsClient(
                base_url=self._base_url, auth=self._auth, requester=self._requester
            )
        return self._documents
