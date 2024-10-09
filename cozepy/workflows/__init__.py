from typing import TYPE_CHECKING, Optional

from cozepy.auth import Auth
from cozepy.request import Requester

if TYPE_CHECKING:
    from .runs import AsyncWorkflowsRunsClient, WorkflowsRunsClient


class WorkflowsClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester
        self._runs: Optional[WorkflowsRunsClient] = None

    @property
    def runs(self) -> "WorkflowsRunsClient":
        if not self._runs:
            from .runs import WorkflowsRunsClient

            self._runs = WorkflowsRunsClient(self._base_url, self._auth, self._requester)
        return self._runs


class AsyncWorkflowsClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester
        self._runs: Optional[AsyncWorkflowsRunsClient] = None

    @property
    def runs(self) -> "AsyncWorkflowsRunsClient":
        if not self._runs:
            from .runs import AsyncWorkflowsRunsClient

            self._runs = AsyncWorkflowsRunsClient(self._base_url, self._auth, self._requester)
        return self._runs
