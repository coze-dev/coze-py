from enum import Enum
from typing import List

from cozepy.auth import Auth
from cozepy.model import AsyncNumberPaged, CozeModel, HTTPRequest, NumberPaged, NumberPagedResponse
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


class _PrivateListWorkspacesData(CozeModel, NumberPagedResponse[Workspace]):
    total_count: int
    workspaces: List[Workspace]

    def get_total(self) -> int:
        return self.total_count

    def get_items(self) -> List[Workspace]:
        return self.workspaces


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

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                headers=headers,
                params={
                    "page_size": i_page_size,
                    "page_num": i_page_num,
                },
                cast=_PrivateListWorkspacesData,
                is_async=False,
                stream=False,
            )

        return NumberPaged(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )


class AsyncWorkspacesClient(object):
    """
    Bot class.
    """

    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester

    async def list(self, *, page_num: int = 1, page_size: int = 20, headers=None) -> AsyncNumberPaged[Workspace]:
        url = f"{self._base_url}/v1/workspaces"

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                headers=headers,
                params={
                    "page_size": i_page_size,
                    "page_num": i_page_num,
                },
                cast=_PrivateListWorkspacesData,
                is_async=False,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )
