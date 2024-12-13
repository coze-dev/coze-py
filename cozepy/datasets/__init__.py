from enum import IntEnum
from typing import TYPE_CHECKING, List, Optional

from cozepy.auth import Auth
from cozepy.model import CozeModel, HTTPRequest, NumberPaged, NumberPagedResponse
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash

if TYPE_CHECKING:
    from .documents import AsyncDatasetsDocumentsClient, DatasetsDocumentsClient


class CreateDatasetResp(CozeModel):
    dataset_id: str


class DatasetFormatType(IntEnum):
    TEXT = 0
    SHEET = 1
    IMAGE = 2


class DatasetStatus(IntEnum):
    Enable = 1
    Disable = 3


class Dataset(CozeModel):
    name: str  # The name of the dataset
    space_id: str  # The ID of the space that the dataset belongs to
    status: DatasetStatus  # The status of the dataset, 0: enable, 3: disable
    can_edit: bool  # Whether the dataset can be edited
    icon_url: str  # The icon URL of the dataset
    doc_count: int  # The count of the documents in the dataset
    file_list: List[str]  # The list of files in the dataset
    hit_count: int  # The count of the hits in the dataset
    # avatar_url:


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
        description: Optional[str] = None,
        icon_file_id: Optional[str] = None,
        format_type: DatasetFormatType = DatasetFormatType.TEXT,
    ) -> CreateDatasetResp:
        """
        Create Dataset

        :param name: The name of the dataset
        :param space_id: The ID of the space that the dataset belongs to
        :param description: The description of the dataset
        :param icon_file_id: The ID of the icon file, uploaded by `coze.files.upload`
        :param format_type: The format type of the dataset, 0: text, 2: image
        """
        url = f"{self._base_url}/v1/datasets"
        body = {
            "name": name,
            "description": description,
            "space_id": space_id,
            "file_id": icon_file_id,
            "format_type": format_type,
        }
        return self._requester.request(
            "post",
            url,
            False,
            CreateDatasetResp,
            body=body,
        )

    def list(
        self,
        *,
        space_id: str,
        name: Optional[str] = None,
        format_type: Optional[DatasetFormatType] = None,
        create_time_order: Optional[str] = None,
        page_num: int = 1,
        page_size: int = 10,
        headers=None,
    ) -> NumberPaged[Dataset]:
        url = f"{self._base_url}/v1/datasets"

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
        description: Optional[str] = None,
        icon_file_id: Optional[str] = None,
        format_type: DatasetFormatType = DatasetFormatType.TEXT,
    ) -> CreateDatasetResp:
        """
        Create Dataset

        :param name: The name of the dataset
        :param space_id: The ID of the space that the dataset belongs to
        :param description: The description of the dataset
        :param icon_file_id: The ID of the icon file, uploaded by `coze.files.upload`
        :param format_type: The format type of the dataset, 0: text, 2: image
        """
        url = f"{self._base_url}/v1/datasets"
        body = {
            "name": name,
            "description": description,
            "space_id": space_id,
            "file_id": icon_file_id,
            "format_type": format_type,
        }
        return await self._requester.arequest(
            "post",
            url,
            False,
            CreateDatasetResp,
            body=body,
        )

    @property
    def documents(self) -> "AsyncDatasetsDocumentsClient":
        if self._documents is None:
            from .documents import AsyncDatasetsDocumentsClient

            self._documents = AsyncDatasetsDocumentsClient(
                base_url=self._base_url, auth=self._auth, requester=self._requester
            )
        return self._documents
