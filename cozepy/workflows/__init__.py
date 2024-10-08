from typing import TYPE_CHECKING

from cozepy.auth import Auth
from cozepy.request import Requester

if TYPE_CHECKING:
    from .runs import AsyncWorkflowsClient as AsyncWorkflowsRunsClient
    from .runs import WorkflowsClient as WorkflowsRunsClient


class WorkflowsClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester
        self._runs = None

    @property
    def runs(self) -> "WorkflowsRunsClient":
        if not self._runs:
            from .runs import WorkflowsClient

            self._runs = WorkflowsClient(self._base_url, self._auth, self._requester)
        return self._runs


class AsyncWorkflowsClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester
        self._runs = None

    @property
    def runs(self) -> "AsyncWorkflowsRunsClient":
        if not self._runs:
            from .runs import AsyncWorkflowsClient

            self._runs = AsyncWorkflowsClient(self._base_url, self._auth, self._requester)
        return self._runs
