from typing import TYPE_CHECKING

from cozepy.auth import Auth
from cozepy.config import COZE_COM_BASE_URL
from cozepy.request import HTTPClient, Requester

if TYPE_CHECKING:
    from .bots import BotsClient
    from .chat import ChatClient
    from .conversations import ConversationsClient
    from .files import FilesClient
    from .knowledge import KnowledgeClient
    from .workflows import WorkflowsClient
    from .workspaces import WorkspacesClient


class Coze(object):
    def __init__(
        self,
        auth: Auth,
        base_url: str = COZE_COM_BASE_URL,
        http_client: HTTPClient = None,
    ):
        self._auth = auth
        self._base_url = base_url
        self._requester = Requester(auth=auth, client=http_client)

        # service client
        self._bots = None
        self._workspaces = None
        self._conversations = None
        self._chat = None
        self._files = None
        self._workflows = None
        self._knowledge = None

    @property
    def bots(self) -> "BotsClient":
        if not self._bots:
            from cozepy.bots import BotsClient

            self._bots = BotsClient(self._base_url, self._auth, self._requester)
        return self._bots

    @property
    def workspaces(self) -> "WorkspacesClient":
        if not self._workspaces:
            from .workspaces import WorkspacesClient

            self._workspaces = WorkspacesClient(self._base_url, self._auth, self._requester)
        return self._workspaces

    @property
    def conversations(self) -> "ConversationsClient":
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
    def files(self) -> "FilesClient":
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

    @property
    def knowledge(self) -> "KnowledgeClient":
        if not self._knowledge:
            from .knowledge import KnowledgeClient

            self._knowledge = KnowledgeClient(self._base_url, self._auth, self._requester)
        return self._knowledge
