from typing import TYPE_CHECKING, List, Optional

from cozepy.bots import PublishStatus
from cozepy.model import AsyncNumberPaged, CozeModel, DynamicStrEnum, HTTPRequest, NumberPaged, NumberPagedResponse
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash

if TYPE_CHECKING:
    from .chat import AsyncWorkflowsChatClient, WorkflowsChatClient
    from .runs import AsyncWorkflowsRunsClient, WorkflowsRunsClient
    from .versions import AsyncWorkflowsVersionsClient, WorkflowsVersionsClient


class WorkflowMode(DynamicStrEnum):
    WORKFLOW = "workflow"
    CHATFLOW = "chatflow"


class WorkflowInfo(CozeModel):
    workflow_id: str
    workflow_name: str
    description: str
    icon_url: str
    app_id: str


class WorkflowDetailInfo(CozeModel):
    """
    工作流详细信息

    包含工作流的完整配置和元数据信息。
    """

    # 工作流ID
    workflow_id: str
    # 工作流名称
    workflow_name: str
    # 工作流描述
    description: str
    # 工作流图标URL
    icon_url: str
    # 应用ID
    app_id: str
    # 工作流模式，可选值：workflow、chatflow
    workflow_mode: str
    # 创建时间，Unix时间戳
    created_at: int
    # 更新时间，Unix时间戳
    updated_at: int
    # 工作流版本号
    version: str
    # 发布状态，可选值：all、published_online、unpublished_draft
    publish_status: str


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
        self._versions: Optional[WorkflowsVersionsClient] = None

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

    @property
    def versions(self) -> "WorkflowsVersionsClient":
        if not self._versions:
            from .versions import WorkflowsVersionsClient

            self._versions = WorkflowsVersionsClient(self._base_url, self._requester)
        return self._versions

    def retrieve(
        self,
        *,
        workflow_id: str,
        **kwargs,
    ) -> WorkflowDetailInfo:
        """
        获取工作流详细信息。

        通过此接口可以获取指定工作流的完整配置和元数据信息。

        docs cn: https://www.coze.cn/docs/developer_guides/get_workflow_info

        :param workflow_id: 工作流ID
        :param kwargs: 额外参数，支持 headers 等
        :return: 返回工作流的详细信息
        """
        url = f"{self._base_url}/v1/workflows/{workflow_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("get", url, False, WorkflowDetailInfo, headers=headers)

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
        self._versions: Optional[AsyncWorkflowsVersionsClient] = None

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

    @property
    def versions(self) -> "AsyncWorkflowsVersionsClient":
        if not self._versions:
            from .versions import AsyncWorkflowsVersionsClient

            self._versions = AsyncWorkflowsVersionsClient(self._base_url, self._requester)
        return self._versions

    async def retrieve(
        self,
        *,
        workflow_id: str,
        **kwargs,
    ) -> WorkflowDetailInfo:
        """
        获取工作流详细信息。

        通过此接口可以获取指定工作流的完整配置和元数据信息。

        docs cn: https://www.coze.cn/docs/developer_guides/get_workflow_info

        :param workflow_id: 工作流ID
        :param kwargs: 额外参数，支持 headers 等
        :return: 返回工作流的详细信息
        """
        url = f"{self._base_url}/v1/workflows/{workflow_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest("get", url, False, WorkflowDetailInfo, headers=headers)

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
