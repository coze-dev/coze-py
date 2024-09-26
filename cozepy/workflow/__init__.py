from typing import TYPE_CHECKING

from cozepy.auth import Auth
from cozepy.request import Requester

if TYPE_CHECKING:
    from .v1 import WorkflowClient as WorkflowClientV1


class WorkflowClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester
        self._v1 = None

    @property
    def v1(self) -> "WorkflowClientV1":
        if not self._v1:
            from .v1 import WorkflowClient

            self._v1 = WorkflowClient(self._base_url, self._auth, self._requester)
        return self._v1
