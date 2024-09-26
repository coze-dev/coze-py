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
        self._workspaces = None
        self._conversations = None
        self._chat = None
        self._files = None
        self._workflows = None

    @property
    def bots(self) -> "BotsClient":
        if not self._bots:
            from cozepy.bots import BotsClient

            self._bots = BotsClient(self._base_url, self._auth, self._requester)
        return self._bots

    @property
    def workspace(self) -> "WorkspacesClient":
        if not self._workspaces:
            from .workspaces import WorkspacesClient

            self._workspaces = WorkspacesClient(self._base_url, self._auth, self._requester)
        return self._workspaces

    @property
    def conversation(self) -> "ConversationsClient":
        if not self._conversations:
            from .conversations import ConversationsClient

            self._conversations = ConversationsClient(self._base_url, self._auth, self._requester)
        return self._conversations

    @property
    def chat(self) -> "ChatClient":
        if not self._chat:
            from cozepy.chat import ChatClient

            self._chat = ChatClient(self._base_url, self._auth, self._requester)
        return self._chat

    @property
    def file(self) -> "FilesClient":
        if not self._files:
            from .files import FilesClient

            self._files = FilesClient(self._base_url, self._auth, self._requester)
        return self._files

    @property
    def workflows(self) -> "WorkflowsClient":
        if not self._workflows:
            from .workflows import WorkflowsClient

            self._workflows = WorkflowsClient(self._base_url, self._auth, self._requester)
        return self._workflows
