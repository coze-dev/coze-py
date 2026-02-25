from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from cozepy.model import AsyncTokenPaged, CozeModel, TokenPaged, TokenPagedResponse
from cozepy.request import HTTPRequest, Requester
from cozepy.util import dump_exclude_none, remove_url_trailing_slash

if TYPE_CHECKING:
    from cozepy.api_apps.events import APIAppsEventsClient, AsyncAPIAppsEventsClient


class AppType(str, Enum):
    NORMAL = "normal"  # 普通回调
    CONNECTOR = "connector"  # 渠道回调


class APIApp(CozeModel):
    id: str
    app_type: AppType
    verify_token: str
    name: Optional[str] = None
    connector_id: Optional[str] = None
    callback_url: Optional[str] = None


class UpdateAPIAppsResp(CozeModel):
    pass


class DeleteAPIAppsResp(CozeModel):
    pass


class _PrivateListAPIAppsData(CozeModel, TokenPagedResponse[APIApp]):
    items: List[APIApp]
    next_page_token: Optional[str] = None
    has_more: bool

    def get_next_page_token(self) -> Optional[str]:
        return self.next_page_token

    def get_has_more(self) -> Optional[bool]:
        return self.has_more

    def get_items(self) -> List[APIApp]:
        return self.items


class APIAppsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._events: Optional[APIAppsEventsClient] = None

    @property
    def events(self) -> "APIAppsEventsClient":
        if not self._events:
            from .events import APIAppsEventsClient

            self._events = APIAppsEventsClient(base_url=self._base_url, requester=self._requester)
        return self._events

    def create(
        self,
        *,
        app_type: AppType,
        name: Optional[str] = None,
        connector_id: Optional[str] = None,
        **kwargs,
    ) -> APIApp:
        """
        创建回调应用

        本 API 用于创建回调应用，支持创建普通回调应用和渠道回调应用。订阅扣子编程回调功能时需要创建回调应用。 接口说明 订阅回调 功能支持开发者通过配置回调应用实时获取扣子编程的事件通知。当 智能体发布 、 智能体删除 、 账单生成 等关键业务事件被触发时，扣子编程将向开发者指定的服务器地址发送回调消息。 回调分为普通回调和渠道回调，具体说明如下： 普通回调应用：开发者在扣子编程中创建回调应用，用于接收扣子编程触发的事件通知。当订阅的事件被触发时，扣子编程会向该回调地址推送回调消息。 渠道回调应用：当渠道入驻扣子编程后，开发者可以在该渠道中创建回调应用，用于接收该渠道中触发的事件通知。当订阅的事件被触发时，扣子编程会向渠道指定的回调地址推送回调消息。 接口限制 扣子个人版中，任何用户均可以创建普通回调应用。仅渠道创建者支持创建对应渠道的回调应用，统一接收该渠道中的回调消息。 扣子企业版（企业标准版、企业旗舰版）中，仅超级管理员和管理员可创建回调应用。

        :param app_type: 必填
        :param name: 回调应用的名称， app_type=normal 时必传
        :param connector_id: app_type=connector 时必传
        """
        url = f"{self._base_url}/v1/api_apps"
        headers: Optional[dict] = kwargs.get("headers")
        body = dump_exclude_none(
            {
                "app_type": app_type,
                "name": name,
                "connector_id": connector_id,
            }
        )
        return self._requester.request("post", url, False, cast=APIApp, headers=headers, body=body)

    def update(
        self,
        *,
        app_id: str,
        name: Optional[str] = None,
        callback_url: Optional[str] = None,
        **kwargs,
    ) -> UpdateAPIAppsResp:
        """
        修改回调应用

        修改回调应用的名称和回调地址。 接口限制 扣子个人版中，仅支持修改本人创建的回调应用。 扣子企业版中，仅超级管理员和管理员可修改回调应用。

        :param app_id: 待修改的回调应用的 ID。你可以通过[查询回调应用列表](https://docs.coze.cn/developer_guides/list_callback_app) API 获取回调应用的 ID。
        """
        url = f"{self._base_url}/v1/api_apps/{app_id}"
        headers: Optional[dict] = kwargs.get("headers")
        body = dump_exclude_none(
            {
                "name": name,
                "callback_url": callback_url,
            }
        )
        return self._requester.request(
            "put",
            url,
            False,
            cast=UpdateAPIAppsResp,
            headers=headers,
            body=body,
        )

    def delete(self, *, app_id: str, **kwargs) -> DeleteAPIAppsResp:
        url = f"{self._base_url}/v1/api_apps/{app_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("delete", url, False, cast=DeleteAPIAppsResp, headers=headers)

    def list(
        self,
        *,
        app_type: Optional[AppType] = None,
        page_token: str = "",
        page_size: int = 20,
        **kwargs,
    ) -> TokenPaged[APIApp]:
        url = f"{self._base_url}/v1/api_apps"
        headers: Optional[dict] = kwargs.get("headers")

        def request_maker(i_page_token: str, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                params=dump_exclude_none(
                    {
                        "app_type": app_type,
                        "page_size": i_page_size,
                        "page_token": i_page_token,
                    }
                ),
                cast=_PrivateListAPIAppsData,
                headers=headers,
                stream=False,
            )

        return TokenPaged(
            page_token=page_token,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )


class AsyncAPIAppsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._events: Optional[AsyncAPIAppsEventsClient] = None

    @property
    def events(self) -> "AsyncAPIAppsEventsClient":
        if not self._events:
            from .events import AsyncAPIAppsEventsClient

            self._events = AsyncAPIAppsEventsClient(base_url=self._base_url, requester=self._requester)
        return self._events

    async def create(
        self,
        *,
        app_type: AppType,
        name: Optional[str] = None,
        connector_id: Optional[str] = None,
        **kwargs,
    ) -> APIApp:
        """
        创建回调应用

        本 API 用于创建回调应用，支持创建普通回调应用和渠道回调应用。订阅扣子编程回调功能时需要创建回调应用。 接口说明 订阅回调 功能支持开发者通过配置回调应用实时获取扣子编程的事件通知。当 智能体发布 、 智能体删除 、 账单生成 等关键业务事件被触发时，扣子编程将向开发者指定的服务器地址发送回调消息。 回调分为普通回调和渠道回调，具体说明如下： 普通回调应用：开发者在扣子编程中创建回调应用，用于接收扣子编程触发的事件通知。当订阅的事件被触发时，扣子编程会向该回调地址推送回调消息。 渠道回调应用：当渠道入驻扣子编程后，开发者可以在该渠道中创建回调应用，用于接收该渠道中触发的事件通知。当订阅的事件被触发时，扣子编程会向渠道指定的回调地址推送回调消息。 接口限制 扣子个人版中，任何用户均可以创建普通回调应用。仅渠道创建者支持创建对应渠道的回调应用，统一接收该渠道中的回调消息。 扣子企业版（企业标准版、企业旗舰版）中，仅超级管理员和管理员可创建回调应用。

        :param app_type: 必填
        :param name: 回调应用的名称， app_type=normal 时必传
        :param connector_id: app_type=connector 时必传
        """
        url = f"{self._base_url}/v1/api_apps"
        headers: Optional[dict] = kwargs.get("headers")
        body = dump_exclude_none(
            {
                "app_type": app_type,
                "name": name,
                "connector_id": connector_id,
            }
        )
        return await self._requester.arequest("post", url, False, cast=APIApp, headers=headers, body=body)

    async def update(
        self,
        *,
        app_id: str,
        name: Optional[str] = None,
        callback_url: Optional[str] = None,
        **kwargs,
    ) -> UpdateAPIAppsResp:
        """
        修改回调应用

        修改回调应用的名称和回调地址。 接口限制 扣子个人版中，仅支持修改本人创建的回调应用。 扣子企业版中，仅超级管理员和管理员可修改回调应用。

        :param app_id: 待修改的回调应用的 ID。你可以通过[查询回调应用列表](https://docs.coze.cn/developer_guides/list_callback_app) API 获取回调应用的 ID。
        """
        url = f"{self._base_url}/v1/api_apps/{app_id}"
        headers: Optional[dict] = kwargs.get("headers")
        body = dump_exclude_none(
            {
                "name": name,
                "callback_url": callback_url,
            }
        )
        return await self._requester.arequest(
            "put",
            url,
            False,
            cast=UpdateAPIAppsResp,
            headers=headers,
            body=body,
        )

    async def delete(self, *, app_id: str, **kwargs) -> DeleteAPIAppsResp:
        url = f"{self._base_url}/v1/api_apps/{app_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest("delete", url, False, cast=DeleteAPIAppsResp, headers=headers)

    async def list(
        self,
        *,
        app_type: Optional[AppType] = None,
        page_token: str = "",
        page_size: int = 20,
        **kwargs,
    ) -> AsyncTokenPaged[APIApp]:
        url = f"{self._base_url}/v1/api_apps"
        headers: Optional[dict] = kwargs.get("headers")

        async def request_maker(i_page_token: str, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "GET",
                url,
                params=dump_exclude_none(
                    {
                        "app_type": app_type,
                        "page_size": i_page_size,
                        "page_token": i_page_token,
                    }
                ),
                cast=_PrivateListAPIAppsData,
                headers=headers,
                stream=False,
            )

        return await AsyncTokenPaged.build(
            page_token=page_token,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )
