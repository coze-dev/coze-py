from cozepy.auth import Auth
from cozepy.request import Requester


class WorkspaceClient(object):
    """
    Bot class.
    """

    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester
        self._v1 = None

    @property
    def v1(self):
        if not self._v1:
            from .v1 import WorkspaceClient

            self._v1 = WorkspaceClient(self._base_url, self._auth, self._requester)
        return self._v1
