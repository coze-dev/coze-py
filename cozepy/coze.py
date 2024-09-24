from typing import TYPE_CHECKING

from cozepy.auth import Auth
from cozepy.config import COZE_COM_BASE_URL
from cozepy.request import Requester

if TYPE_CHECKING:
    from .bot import BotClient
    from .workspace import WorkspaceClient
    from .conversation import ConversationClient
    from .chat import ChatClient


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
        self._conversation = None
        self._chat = None

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

    @property
    def conversation(self) -> "ConversationClient":
        if not self._conversation:
            from cozepy.conversation import ConversationClient

            self._conversation = ConversationClient(self._base_url, self._auth, self._requester)
        return self._conversation

    @property
    def chat(self) -> "ChatClient":
        if not self._chat:
            from cozepy.chat import ChatClient

            self._chat = ChatClient(self._base_url, self._auth, self._requester)
        return self._chat
