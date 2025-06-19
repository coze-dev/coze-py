from typing import TYPE_CHECKING, List, Optional

from cozepy.model import AsyncNumberPaged, CozeModel, DynamicStrEnum, HTTPRequest, NumberPaged, NumberPagedResponse
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash

if TYPE_CHECKING:
    from .members import AsyncWorkspacesMembersClient, WorkspacesMembersClient


class WorkspaceRoleType(DynamicStrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class WorkspaceType(DynamicStrEnum):
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
    # enterprise id
    enterprise_id: str


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
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

        self._members: Optional[WorkspacesMembersClient] = None

    @property
    def members(self) -> "WorkspacesMembersClient":
        if not self._members:
            from .members import WorkspacesMembersClient

            self._members = WorkspacesMembersClient(self._base_url, self._requester)
        return self._members

    def list(
        self,
        *,
        user_id: Optional[str] = None,
        coze_account_id: Optional[str] = None,
        page_num: int = 1,
        page_size: int = 20,
        **kwargs,
    ) -> NumberPaged[Workspace]:
        url = f"{self._base_url}/v1/workspaces"
        headers: Optional[dict] = kwargs.get("headers")

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                headers=headers,
                params=remove_none_values(
                    {
                        "page_size": i_page_size,
                        "page_num": i_page_num,
                        "user_id": user_id,
                        "coze_account_id": coze_account_id,
                    }
                ),
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
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

        self._members: Optional[AsyncWorkspacesMembersClient] = None

    @property
    def members(self) -> "AsyncWorkspacesMembersClient":
        if not self._members:
            from .members import AsyncWorkspacesMembersClient

            self._members = AsyncWorkspacesMembersClient(self._base_url, self._requester)
        return self._members

    async def list(
        self,
        *,
        user_id: Optional[str] = None,
        coze_account_id: Optional[str] = None,
        page_num: int = 1,
        page_size: int = 20,
        **kwargs,
    ) -> AsyncNumberPaged[Workspace]:
        url = f"{self._base_url}/v1/workspaces"
        headers: Optional[dict] = kwargs.get("headers")

        async def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "GET",
                url,
                headers=headers,
                params=remove_none_values(
                    {
                        "page_size": i_page_size,
                        "page_num": i_page_num,
                        "user_id": user_id,
                        "coze_account_id": coze_account_id,
                    }
                ),
                cast=_PrivateListWorkspacesData,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )
