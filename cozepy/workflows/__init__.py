from typing import TYPE_CHECKING, Optional

from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash

if TYPE_CHECKING:
    from .chat import AsyncWorkflowsChatClient, WorkflowsChatClient
    from .runs import AsyncWorkflowsRunsClient, WorkflowsRunsClient


class WorkflowsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._runs: Optional[WorkflowsRunsClient] = None
        self._chat: Optional[WorkflowsChatClient] = None

    @property
    def runs(self) -> "WorkflowsRunsClient":
        if not self._runs:
            from .runs import WorkflowsRunsClient

            self._runs = WorkflowsRunsClient(self._base_url, self._requester)
        return self._runs

    @property
    def chat(self) -> "WorkflowsChatClient":
        if not self._chat:
            from .chat import WorkflowsChatClient

            self._chat = WorkflowsChatClient(self._base_url, self._requester)
        return self._chat


class AsyncWorkflowsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._runs: Optional[AsyncWorkflowsRunsClient] = None
        self._chat: Optional[AsyncWorkflowsChatClient] = None

    @property
    def runs(self) -> "AsyncWorkflowsRunsClient":
        if not self._runs:
            from .runs import AsyncWorkflowsRunsClient

            self._runs = AsyncWorkflowsRunsClient(self._base_url, self._requester)
        return self._runs

    @property
    def chat(self) -> "AsyncWorkflowsChatClient":
        if not self._chat:
            from .chat import AsyncWorkflowsChatClient

            self._chat = AsyncWorkflowsChatClient(self._base_url, self._requester)
        return self._chat
