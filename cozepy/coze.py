import warnings
from typing import TYPE_CHECKING, Optional

from cozepy.auth import Auth, SyncAuth
from cozepy.config import COZE_COM_BASE_URL
from cozepy.request import AsyncHTTPClient, Requester, SyncHTTPClient
from cozepy.util import remove_url_trailing_slash

if TYPE_CHECKING:
    from .api_apps import APIAppsClient, AsyncAPIAppsClient
    from .apps import AppsClient, AsyncAppsClient
    from .audio import AsyncAudioClient, AudioClient
    from .bots import AsyncBotsClient, BotsClient
    from .chat import AsyncChatClient, ChatClient
    from .conversations import AsyncConversationsClient, ConversationsClient
    from .datasets import AsyncDatasetsClient, DatasetsClient
    from .enterprises import AsyncEnterprisesClient, EnterprisesClient
    from .files import AsyncFilesClient, FilesClient
    from .folders import AsyncFoldersClient, FoldersClient
    from .knowledge import AsyncKnowledgeClient, KnowledgeClient  # deprecated
    from .templates import AsyncTemplatesClient, TemplatesClient
    from .users import AsyncUsersClient, UsersClient
    from .variables import AsyncVariablesClient, VariablesClient
    from .websockets import AsyncWebsocketsClient, WebsocketsClient
    from .workflows import AsyncWorkflowsClient, WorkflowsClient
    from .workspaces import AsyncWorkspacesClient, WorkspacesClient


class Coze(object):
    def __init__(
        self,
        auth: Auth,
        base_url: str = COZE_COM_BASE_URL,
        http_client: Optional[SyncHTTPClient] = None,
    ):
        self._auth = auth
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = Requester(auth=auth, sync_client=http_client)

        # service client
        self._bots: Optional[BotsClient] = None
        self._workspaces: Optional[WorkspacesClient] = None
        self._conversations: Optional[ConversationsClient] = None
        self._chat: Optional[ChatClient] = None
        self._files: Optional[FilesClient] = None
        self._workflows: Optional[WorkflowsClient] = None
        self._knowledge: Optional[KnowledgeClient] = None  # deprecated
        self._datasets: Optional[DatasetsClient] = None
        self._audio: Optional[AudioClient] = None
        self._templates: Optional[TemplatesClient] = None
        self._users: Optional[UsersClient] = None
        self._websockets: Optional[WebsocketsClient] = None
        self._variables: Optional[VariablesClient] = None
        self._apps: Optional[AppsClient] = None
        self._enterprises: Optional[EnterprisesClient] = None
        self._api_apps: Optional[APIAppsClient] = None
        self._folders: Optional[FoldersClient] = None

    @property
    def bots(self) -> "BotsClient":
        if not self._bots:
            from cozepy.bots import BotsClient

            self._bots = BotsClient(self._base_url, self._requester)
        return self._bots

    @property
    def workspaces(self) -> "WorkspacesClient":
        if not self._workspaces:
            from .workspaces import WorkspacesClient

            self._workspaces = WorkspacesClient(self._base_url, self._requester)
        return self._workspaces

    @property
    def conversations(self) -> "ConversationsClient":
        if not self._conversations:
            from .conversations import ConversationsClient

            self._conversations = ConversationsClient(self._base_url, self._requester)
        return self._conversations

    @property
    def chat(self) -> "ChatClient":
        if not self._chat:
            from cozepy.chat import ChatClient

            self._chat = ChatClient(self._base_url, self._requester)
        return self._chat

    @property
    def files(self) -> "FilesClient":
        if not self._files:
            from .files import FilesClient

            self._files = FilesClient(self._base_url, self._requester)
        return self._files

    @property
    def workflows(self) -> "WorkflowsClient":
        if not self._workflows:
            from .workflows import WorkflowsClient

            self._workflows = WorkflowsClient(self._base_url, self._requester)
        return self._workflows

    @property
    def knowledge(self) -> "KnowledgeClient":
        warnings.warn(
            "The 'coze.knowledge' module is deprecated and will be removed in a future version. "
            "Please use 'coze.datasets' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        if not self._knowledge:
            from .knowledge import KnowledgeClient

            self._knowledge = KnowledgeClient(self._base_url, self._requester)
        return self._knowledge

    @property
    def datasets(self) -> "DatasetsClient":
        if not self._datasets:
            from .datasets import DatasetsClient

            self._datasets = DatasetsClient(self._base_url, self._requester)
        return self._datasets

    @property
    def audio(self) -> "AudioClient":
        if not self._audio:
            from .audio import AudioClient

            self._audio = AudioClient(self._base_url, self._requester)
        return self._audio

    @property
    def templates(self) -> "TemplatesClient":
        if not self._templates:
            from .templates import TemplatesClient

            self._templates = TemplatesClient(self._base_url, self._requester)
        return self._templates

    @property
    def users(self) -> "UsersClient":
        if not self._users:
            from .users import UsersClient

            self._users = UsersClient(self._base_url, self._requester)
        return self._users

    @property
    def websockets(self) -> "WebsocketsClient":
        if not self._websockets:
            from .websockets import WebsocketsClient

            self._websockets = WebsocketsClient(self._base_url, self._requester)
        return self._websockets

    @property
    def variables(self) -> "VariablesClient":
        if not self._variables:
            from .variables import VariablesClient

            self._variables = VariablesClient(self._base_url, self._requester)
        return self._variables

    @property
    def apps(self) -> "AppsClient":
        if not self._apps:
            from .apps import AppsClient

            self._apps = AppsClient(self._base_url, self._requester)
        return self._apps

    @property
    def enterprises(self) -> "EnterprisesClient":
        if not self._enterprises:
            from .enterprises import EnterprisesClient

            self._enterprises = EnterprisesClient(self._base_url, self._requester)
        return self._enterprises

    @property
    def api_apps(self) -> "APIAppsClient":
        if not self._api_apps:
            from .api_apps import APIAppsClient

            self._api_apps = APIAppsClient(self._base_url, self._requester)
        return self._api_apps

    @property
    def folders(self) -> "FoldersClient":
        if not self._folders:
            from .folders import FoldersClient

            self._folders = FoldersClient(self._base_url, self._requester)
        return self._folders


class AsyncCoze(object):
    def __init__(
        self,
        auth: Auth,
        base_url: str = COZE_COM_BASE_URL,
        http_client: Optional[AsyncHTTPClient] = None,
    ):
        self._auth = auth
        self._base_url = remove_url_trailing_slash(base_url)
        if isinstance(auth, SyncAuth):
            warnings.warn(
                "The 'coze.SyncAuth' use for AsyncCoze is deprecated and will be removed in a future version. "
                "Please use 'coze.AsyncAuth' instead.",
                DeprecationWarning,
                stacklevel=2,
            )

        self._requester = Requester(auth=auth, async_client=http_client)

        # service client
        self._bots: Optional[AsyncBotsClient] = None
        self._chat: Optional[AsyncChatClient] = None
        self._conversations: Optional[AsyncConversationsClient] = None
        self._files: Optional[AsyncFilesClient] = None
        self._knowledge: Optional[AsyncKnowledgeClient] = None  # deprecated
        self._datasets: Optional[AsyncDatasetsClient] = None
        self._workflows: Optional[AsyncWorkflowsClient] = None
        self._workspaces: Optional[AsyncWorkspacesClient] = None
        self._audio: Optional[AsyncAudioClient] = None
        self._templates: Optional[AsyncTemplatesClient] = None
        self._users: Optional[AsyncUsersClient] = None
        self._websockets: Optional[AsyncWebsocketsClient] = None
        self._variables: Optional[AsyncVariablesClient] = None
        self._apps: Optional[AsyncAppsClient] = None
        self._enterprises: Optional[AsyncEnterprisesClient] = None
        self._api_apps: Optional[AsyncAPIAppsClient] = None
        self._folders: Optional[AsyncFoldersClient] = None

    @property
    def bots(self) -> "AsyncBotsClient":
        if not self._bots:
            from cozepy.bots import AsyncBotsClient

            self._bots = AsyncBotsClient(self._base_url, self._requester)
        return self._bots

    @property
    def chat(self) -> "AsyncChatClient":
        if not self._chat:
            from cozepy.chat import AsyncChatClient

            self._chat = AsyncChatClient(self._base_url, self._requester)
        return self._chat

    @property
    def conversations(self) -> "AsyncConversationsClient":
        if not self._conversations:
            from .conversations import AsyncConversationsClient

            self._conversations = AsyncConversationsClient(self._base_url, self._requester)
        return self._conversations

    @property
    def files(self) -> "AsyncFilesClient":
        if not self._files:
            from .files import AsyncFilesClient

            self._files = AsyncFilesClient(self._base_url, self._requester)
        return self._files

    @property
    def knowledge(self) -> "AsyncKnowledgeClient":
        warnings.warn(
            "The 'coze.knowledge' module is deprecated and will be removed in a future version. "
            "Please use 'coze.datasets' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        if not self._knowledge:
            from .knowledge import AsyncKnowledgeClient

            self._knowledge = AsyncKnowledgeClient(self._base_url, self._requester)
        return self._knowledge

    @property
    def datasets(self) -> "AsyncDatasetsClient":
        if not self._datasets:
            from .datasets import AsyncDatasetsClient

            self._datasets = AsyncDatasetsClient(self._base_url, self._requester)
        return self._datasets

    @property
    def workflows(self) -> "AsyncWorkflowsClient":
        if not self._workflows:
            from .workflows import AsyncWorkflowsClient

            self._workflows = AsyncWorkflowsClient(self._base_url, self._requester)
        return self._workflows

    @property
    def workspaces(self) -> "AsyncWorkspacesClient":
        if not self._workspaces:
            from .workspaces import AsyncWorkspacesClient

            self._workspaces = AsyncWorkspacesClient(self._base_url, self._requester)
        return self._workspaces

    @property
    def audio(self) -> "AsyncAudioClient":
        if not self._audio:
            from .audio import AsyncAudioClient

            self._audio = AsyncAudioClient(self._base_url, self._requester)
        return self._audio

    @property
    def templates(self) -> "AsyncTemplatesClient":
        if not self._templates:
            from .templates import AsyncTemplatesClient

            self._templates = AsyncTemplatesClient(self._base_url, self._requester)
        return self._templates

    @property
    def users(self) -> "AsyncUsersClient":
        if not self._users:
            from .users import AsyncUsersClient

            self._users = AsyncUsersClient(self._base_url, self._requester)
        return self._users

    @property
    def websockets(self) -> "AsyncWebsocketsClient":
        if not self._websockets:
            from .websockets import AsyncWebsocketsClient

            self._websockets = AsyncWebsocketsClient(self._base_url, self._requester)
        return self._websockets

    @property
    def variables(self) -> "AsyncVariablesClient":
        if not self._variables:
            from .variables import AsyncVariablesClient

            self._variables = AsyncVariablesClient(self._base_url, self._requester)
        return self._variables

    @property
    def apps(self) -> "AsyncAppsClient":
        if not self._apps:
            from .apps import AsyncAppsClient

            self._apps = AsyncAppsClient(self._base_url, self._requester)
        return self._apps

    @property
    def enterprises(self) -> "AsyncEnterprisesClient":
        if not self._enterprises:
            from .enterprises import AsyncEnterprisesClient

            self._enterprises = AsyncEnterprisesClient(self._base_url, self._requester)
        return self._enterprises

    @property
    def api_apps(self) -> "AsyncAPIAppsClient":
        if not self._api_apps:
            from .api_apps import AsyncAPIAppsClient

            self._api_apps = AsyncAPIAppsClient(self._base_url, self._requester)
        return self._api_apps

    @property
    def folders(self) -> "AsyncFoldersClient":
        if not self._folders:
            from .folders import AsyncFoldersClient

            self._folders = AsyncFoldersClient(self._base_url, self._requester)
        return self._folders
