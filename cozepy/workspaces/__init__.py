from enum import Enum
from typing import List

from cozepy.auth import Auth
from cozepy.model import CozeModel, NumberPaged
from cozepy.request import Requester


class WorkspaceRoleType(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class WorkspaceType(str, Enum):
    PERSONAL = "personal"
    TEAM = "team"


class Workspace(CozeModel):
    # workspace id
    id: str
    # workspace name
    name: str
    # workspace icon url
    icon_url: str
    # user in workspace role type
    role_type: WorkspaceRoleType
    # workspace type
    workspace_type: WorkspaceType


class WorkspacesClient(object):
    """
    Bot class.
    """

    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester

    def list(self, *, page_num: int = 1, page_size: int = 20, headers=None) -> NumberPaged[Workspace]:
        url = f"{self._base_url}/v1/workspaces"
        params = {
            "page_size": page_size,
            "page_num": page_num,
        }
        data = self._requester.request(
            "get",
            url,
            self._PrivateListPublishedBotsV1Data,
            headers=headers,
            params=params,
        )
        return NumberPaged(
            items=data.workspaces,
            page_num=page_num,
            page_size=page_size,
            total=data.total_count,
        )

    class _PrivateListPublishedBotsV1Data(CozeModel):
        total_count: int
        workspaces: List[Workspace]
