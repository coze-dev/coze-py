import warnings
from typing import TYPE_CHECKING, Optional

from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash

if TYPE_CHECKING:
    from .documents import AsyncDocumentsClient, DocumentsClient


class KnowledgeClient(object):
    def __init__(self, base_url: str, requester: Requester):
        warnings.warn(
            "The 'coze.knowledge' module is deprecated and will be removed in a future version. "
            "Please use 'coze.datasets' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._documents: Optional[DocumentsClient] = None

    @property
    def documents(self) -> "DocumentsClient":
        warnings.warn(
            "The 'coze.knowledge.documents' module is deprecated and will be removed in a future version. "
            "Please use 'coze.datasets.documents' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        if self._documents is None:
            from .documents import DocumentsClient

            self._documents = DocumentsClient(base_url=self._base_url, requester=self._requester)
        return self._documents


class AsyncKnowledgeClient(object):
    def __init__(self, base_url: str, requester: Requester):
        warnings.warn(
            "The 'coze.knowledge' module is deprecated and will be removed in a future version. "
            "Please use 'coze.datasets' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._documents: Optional[AsyncDocumentsClient] = None

    @property
    def documents(self) -> "AsyncDocumentsClient":
        warnings.warn(
            "The 'coze.knowledge.documents' module is deprecated and will be removed in a future version. "
            "Please use 'coze.datasets.documents' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        if self._documents is None:
            from .documents import AsyncDocumentsClient

            self._documents = AsyncDocumentsClient(base_url=self._base_url, requester=self._requester)
        return self._documents
