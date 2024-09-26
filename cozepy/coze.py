from typing import TYPE_CHECKING

from cozepy.auth import Auth
from cozepy.config import COZE_COM_BASE_URL
from cozepy.request import Requester

if TYPE_CHECKING:
    from .bots import BotsClient
    from .workspaces import WorkspacesClient
    from .conversations import ConversationsClient
    from .chat import ChatClient
    from .files import FilesClient
    from .workflows import WorkflowsClient


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
        self._bots = None
        self._workspace = None
        self._conversation = None
        self._chat = None
        self._file = None
        self._workflow = None

    @property
    def bots(self) -> "BotsClient":
        if not self._bots:
            from cozepy.bots import BotsClient

            self._bots = BotsClient(self._base_url, self._auth, self._requester)
        return self._bots

    @property
    def workspace(self) -> "WorkspacesClient":
        if not self._workspace:
            from .workspaces import WorkspacesClient

            self._workspace = WorkspacesClient(self._base_url, self._auth, self._requester)
        return self._workspace

    @property
    def conversation(self) -> "ConversationsClient":
        if not self._conversation:
            from .conversations import ConversationsClient

            self._conversation = ConversationsClient(self._base_url, self._auth, self._requester)
        return self._conversation

    @property
    def chat(self) -> "ChatClient":
        if not self._chat:
            from cozepy.chat import ChatClient

            self._chat = ChatClient(self._base_url, self._auth, self._requester)
        return self._chat

    @property
    def file(self) -> "FilesClient":
        if not self._file:
            from .files import FilesClient

            self._file = FilesClient(self._base_url, self._auth, self._requester)
        return self._file

    @property
    def workflow(self) -> "WorkflowsClient":
        if not self._workflow:
            from .workflow import WorkflowsClient

            self._workflow = WorkflowsClient(self._base_url, self._auth, self._requester)
        return self._workflow
