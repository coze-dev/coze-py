from enum import Enum
from typing import List, Optional

from cozepy.model import AsyncNumberPaged, CozeModel, HTTPRequest, NumberPaged, NumberPagedResponse
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


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

    def get_total(self) -> Optional[int]:
        return self.total_count

    def get_has_more(self) -> Optional[bool]:
        return None

    def get_items(self) -> List[Workspace]:
        return self.workspaces


class WorkspacesClient(object):
    """
    Bot class.
    """

    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
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

    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def list(self, *, page_num: int = 1, page_size: int = 20, headers=None) -> AsyncNumberPaged[Workspace]:
        url = f"{self._base_url}/v1/workspaces"

        async def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "GET",
                url,
                headers=headers,
                params={
                    "page_size": i_page_size,
                    "page_num": i_page_num,
                },
                cast=_PrivateListWorkspacesData,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )
