from enum import IntEnum
from typing import TYPE_CHECKING, Optional

from cozepy.auth import Auth
from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash

if TYPE_CHECKING:
    from .documents import AsyncDatasetsDocumentsClient, DatasetsDocumentsClient


class CreateDatasetResp(CozeModel):
    dataset_id: str


class DatasetFormatType(IntEnum):
    TEXT = 0
    IMAGE = 2


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
