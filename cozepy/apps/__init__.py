from typing import List, Optional

from cozepy.bots import PublishStatus
from cozepy.model import AsyncNumberPaged, CozeModel, NumberPaged, NumberPagedResponse
from cozepy.request import HTTPRequest, Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash


class SimpleApp(CozeModel):
    id: str
    name: str
    description: str
    icon_url: str
    is_published: bool
    owner_user_id: str
    updated_at: int

    folder_id: Optional[str] = None
    published_at: Optional[int] = None


class _PrivateListAppsData(CozeModel, NumberPagedResponse[SimpleApp]):
    items: List[SimpleApp]
    total: int

    def get_total(self) -> Optional[int]:
        return self.total

    def get_has_more(self) -> Optional[bool]:
        return None

    def get_items(self) -> List[SimpleApp]:
        return self.items


class AppsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def list(
        self,
        *,
        workspace_id: str,
        publish_status: Optional[PublishStatus] = None,
        connector_id: Optional[str] = None,
        page_num: int = 1,
        page_size: int = 20,
        **kwargs,
    ) -> NumberPaged[SimpleApp]:
        """
        :param workspace_id: The ID of the workspace.
        App 所在的 workspace ID。workspace ID 是 workspace 的唯一标识。
        :param page_num: Pagination size. The default is 20, meaning that 20 data entries are returned per page.
        分页大小。默认为 20，即每页返回 20 条数据。
        :param page_size: Page number for paginated queries. The default is 1,
        meaning that the data return starts from the first page.
        分页查询时的页码。默认为 1，即从第一页数据开始返回。
        :return: Specify the list of Apps in the workspace.
        指定 workspace 的 App 列表。
        """
        url = f"{self._base_url}/v1/apps"
        headers: Optional[dict] = kwargs.get("headers")

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                params=remove_none_values(
                    {
                        "workspace_id": workspace_id,
                        "page_size": i_page_size,
                        "page_index": i_page_num,
                        "publish_status": publish_status.value if publish_status else None,
                        "connector_id": connector_id,
                    }
                ),
                headers=headers,
                cast=_PrivateListAppsData,
                stream=False,
            )

        return NumberPaged(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )


class AsyncAppsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def list(
        self,
        *,
        workspace_id: str,
        publish_status: Optional[PublishStatus] = None,
        connector_id: Optional[str] = None,
        page_num: int = 1,
        page_size: int = 20,
        **kwargs,
    ) -> AsyncNumberPaged[SimpleApp]:
        """
        :param workspace_id: The ID of the workspace.
        App 所在的 workspace ID。workspace ID 是 workspace 的唯一标识。
        :param page_num: Pagination size. The default is 20, meaning that 20 data entries are returned per page.
        分页大小。默认为 20，即每页返回 20 条数据。
        :param page_size: Page number for paginated queries. The default is 1,
        meaning that the data return starts from the first page.
        分页查询时的页码。默认为 1，即从第一页数据开始返回。
        :return: Specify the list of Apps in the workspace.
        指定 workspace 的 App 列表。
        """
        url = f"{self._base_url}/v1/apps"
        headers: Optional[dict] = kwargs.get("headers")

        async def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "GET",
                url,
                params=remove_none_values(
                    {
                        "workspace_id": workspace_id,
                        "page_size": i_page_size,
                        "page_index": i_page_num,
                        "publish_status": publish_status.value if publish_status else None,
                        "connector_id": connector_id,
                    }
                ),
                headers=headers,
                cast=_PrivateListAppsData,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )
