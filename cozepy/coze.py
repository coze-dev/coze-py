from typing import TYPE_CHECKING

from cozepy.auth import Auth
from cozepy.config import COZE_COM_BASE_URL
from cozepy.request import Requester

if TYPE_CHECKING:
    from .bot import BotClient
    from .workspace import WorkspaceClient


class Coze(object):
    def __init__(
        self,
        auth: Auth,
        base_url: str = COZE_COM_BASE_URL,
    ):
        self._auth = auth
        self._base_url = base_url
        self._requester = Requester(auth=auth)

        # service client
        self._bot = None
        self._workspace = None

    @property
    def bot(self) -> "BotClient":
        if not self._bot:
            from cozepy.bot import BotClient

            self._bot = BotClient(self._base_url, self._auth, self._requester)
        return self._bot

    @property
    def workspace(self) -> "WorkspaceClient":
        if not self._workspace:
            from cozepy.workspace import WorkspaceClient

            self._workspace = WorkspaceClient(self._base_url, self._auth, self._requester)
        return self._workspace
