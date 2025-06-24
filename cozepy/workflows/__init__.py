from typing import TYPE_CHECKING, List, Optional

from cozepy.bots import PublishStatus
from cozepy.model import AsyncNumberPaged, CozeModel, DynamicStrEnum, HTTPRequest, NumberPaged, NumberPagedResponse
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash

if TYPE_CHECKING:
    from .chat import AsyncWorkflowsChatClient, WorkflowsChatClient
    from .runs import AsyncWorkflowsRunsClient, WorkflowsRunsClient


class WorkflowMode(DynamicStrEnum):
    WORKFLOW = "workflow"
    CHATFLOW = "chatflow"


class WorkflowInfo(CozeModel):
    workflow_id: str
    workflow_name: str
    description: str
    icon_url: str
    app_id: str


class _PrivateListWorkflowData(CozeModel, NumberPagedResponse[WorkflowInfo]):
    items: List[WorkflowInfo]
    has_more: bool

    def get_total(self) -> Optional[int]:
        return None

    def get_has_more(self) -> Optional[bool]:
        return self.has_more

    def get_items(self) -> List[WorkflowInfo]:
        return self.items


class WorkflowsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._runs: Optional[WorkflowsRunsClient] = None
        self._chat: Optional[WorkflowsChatClient] = None

    @property
    def runs(self) -> "WorkflowsRunsClient":
        if not self._runs:
            from .runs import WorkflowsRunsClient

            self._runs = WorkflowsRunsClient(self._base_url, self._requester)
        return self._runs

    @property
    def chat(self) -> "WorkflowsChatClient":
        if not self._chat:
            from .chat import WorkflowsChatClient

            self._chat = WorkflowsChatClient(self._base_url, self._requester)
        return self._chat

    def list(
        self,
        *,
        workspace_id: Optional[str] = None,
        workflow_mode: Optional[WorkflowMode] = None,
        app_id: Optional[str] = None,
        publish_status: Optional[PublishStatus] = None,
        page_num: int = 1,
        page_size: int = 100,
    ) -> NumberPaged[WorkflowInfo]:
        url = f"{self._base_url}/v1/workflows"

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                params=remove_none_values(
                    {
                        "workspace_id": workspace_id,
                        "workflow_mode": workflow_mode,
                        "app_id": app_id,
                        "publish_status": publish_status,
                        "page_num": i_page_num,
                        "page_size": i_page_size,
                    }
                ),
                cast=_PrivateListWorkflowData,
                stream=False,
            )

        return NumberPaged(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )


class AsyncWorkflowsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._runs: Optional[AsyncWorkflowsRunsClient] = None
        self._chat: Optional[AsyncWorkflowsChatClient] = None

    @property
    def runs(self) -> "AsyncWorkflowsRunsClient":
        if not self._runs:
            from .runs import AsyncWorkflowsRunsClient

            self._runs = AsyncWorkflowsRunsClient(self._base_url, self._requester)
        return self._runs

    @property
    def chat(self) -> "AsyncWorkflowsChatClient":
        if not self._chat:
            from .chat import AsyncWorkflowsChatClient

            self._chat = AsyncWorkflowsChatClient(self._base_url, self._requester)
        return self._chat

    async def list(
        self,
        *,
        workspace_id: Optional[str] = None,
        workflow_mode: Optional[WorkflowMode] = None,
        app_id: Optional[str] = None,
        publish_status: Optional[PublishStatus] = None,
        page_num: int = 1,
        page_size: int = 100,
        **kwargs,
    ) -> AsyncNumberPaged[WorkflowInfo]:
        url = f"{self._base_url}/v1/workflows"
        headers: Optional[dict] = kwargs.get("headers")

        async def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "GET",
                url,
                params=remove_none_values(
                    {
                        "workspace_id": workspace_id,
                        "workflow_mode": workflow_mode,
                        "app_id": app_id,
                        "publish_status": publish_status,
                        "page_num": i_page_num,
                        "page_size": i_page_size,
                    }
                ),
                headers=headers,
                cast=_PrivateListWorkflowData,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )
