from typing import List, Optional

from cozepy.bots import PublishStatus
from cozepy.model import AsyncTokenPaged, CozeModel, HTTPRequest, TokenPaged, TokenPagedResponse
from cozepy.request import Requester
from cozepy.util import dump_exclude_none, remove_none_values, remove_url_trailing_slash


class WorkflowUserInfo(CozeModel):
    # 用户ID
    id: str

    # 用户名称
    name: str


class WorkflowVersionInfo(CozeModel):
    # 版本号
    version: str

    # 版本描述
    description: str

    # 创建时间，Unix时间戳
    created_at: str

    # 更新时间，Unix时间戳
    updated_at: str

    # 工作流ID
    workflow_id: str

    # 创建者信息
    creator: WorkflowUserInfo


class _PrivateListWorkflowVersionData(CozeModel, TokenPagedResponse[WorkflowVersionInfo]):
    items: List[WorkflowVersionInfo]
    has_more: bool
    next_page_token: Optional[str] = None

    def get_next_page_token(self) -> Optional[str]:
        return self.next_page_token

    def get_has_more(self) -> Optional[bool]:
        return self.has_more

    def get_items(self) -> List[WorkflowVersionInfo]:
        return self.items


class WorkflowsVersionsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def list(
        self,
        *,
        workflow_id: str,
        publish_status: Optional[PublishStatus] = None,
        page_size: int = 10,
        page_token: Optional[str] = None,
        **kwargs,
    ) -> TokenPaged[WorkflowVersionInfo]:
        """
        查询工作流版本列表。

        通过此接口可以查询指定工作流下的所有版本信息。

        docs cn: https://www.coze.cn/docs/developer_guides/list_workflow_version

        :param workflow_id: 工作流ID
        :param publish_status: 发布状态，支持 all(全部)、published_online(已发布，默认)、unpublished_draft(未发布)
        :param page_size: 每页返回的版本数量，取值范围为 1~30，默认为 10
        :param page_token: 分页标记，获取下一页时传入上一页返回的 next_page_token 值
        :param kwargs: 额外参数，支持 headers 等
        :return: 返回工作流版本信息的分页列表
        """
        url = f"{self._base_url}/v1/workflows/{workflow_id}/versions"
        headers: Optional[dict] = kwargs.get("headers")

        def request_maker(i_page_token: str, i_page_size: int) -> HTTPRequest:
            params = dump_exclude_none(
                {
                    "publish_status": publish_status,
                    "page_size": i_page_size,
                    "page_token": i_page_token,
                }
            )
            return self._requester.make_request(
                "GET",
                url,
                params=params,
                headers=headers,
                cast=_PrivateListWorkflowVersionData,
                stream=False,
            )

        return TokenPaged(
            page_token=page_token or "",
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )


class AsyncWorkflowsVersionsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def list(
        self,
        *,
        workflow_id: str,
        publish_status: Optional[PublishStatus] = None,
        page_size: int = 10,
        page_token: Optional[str] = None,
        **kwargs,
    ) -> AsyncTokenPaged[WorkflowVersionInfo]:
        """
        查询工作流版本列表。

        通过此接口可以查询指定工作流下的所有版本信息。

        docs cn: https://www.coze.cn/docs/developer_guides/list_workflow_version

        :param workflow_id: 工作流ID
        :param publish_status: 发布状态，支持 all(全部)、published_online(已发布，默认)、unpublished_draft(未发布)
        :param page_size: 每页返回的版本数量，取值范围为 1~30，默认为 10
        :param page_token: 分页标记，获取下一页时传入上一页返回的 next_page_token 值
        :param kwargs: 额外参数，支持 headers 等
        :return: 返回工作流版本信息的分页列表
        """
        url = f"{self._base_url}/v1/workflows/{workflow_id}/versions"
        headers: Optional[dict] = kwargs.get("headers")

        async def request_maker(i_page_token: str, i_page_size: int) -> HTTPRequest:
            params = remove_none_values(
                {
                    "publish_status": publish_status,
                    "page_size": i_page_size,
                    "page_token": i_page_token,
                }
            )
            return await self._requester.amake_request(
                "GET",
                url,
                params=params,
                headers=headers,
                cast=_PrivateListWorkflowVersionData,
                stream=False,
            )

        return await AsyncTokenPaged.build(
            page_token=page_token or "",
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )
