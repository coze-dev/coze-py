from typing import TYPE_CHECKING, Optional

from cozepy.auth import Auth
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash

if TYPE_CHECKING:
    from .documents import AsyncDatasetsDocumentsClient, DatasetsDocumentsClient


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


class AsyncDatasetsClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._auth = auth
        self._requester = requester
        self._documents: Optional[AsyncDatasetsDocumentsClient] = None

    @property
    def documents(self) -> "AsyncDatasetsDocumentsClient":
        if self._documents is None:
            from .documents import AsyncDatasetsDocumentsClient

            self._documents = AsyncDatasetsDocumentsClient(
                base_url=self._base_url, auth=self._auth, requester=self._requester
            )
        return self._documents
