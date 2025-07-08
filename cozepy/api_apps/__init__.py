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

            self._events = APIAppsEventsClient(self._base_url, self._requester)
        return self._events

    def create(
        self,
        *,
        app_type: AppType,
        name: Optional[str] = None,
        connector_id: Optional[str] = None,
        **kwargs,
    ) -> APIApp:
        """create api app

        :param app_type: The type of the api app.
        :param name: The name of the api app, required when app_type is normal.
        :param connector_id: The connector id of the api app, required when app_type is connector.
        :return: The api app object.
        """
        url = f"{self._base_url}/v1/api_apps"
        body = dump_exclude_none(
            {
                "app_type": app_type,
                "name": name,
                "connector_id": connector_id,
            }
        )
        headers: Optional[dict] = kwargs.get("headers")

        return self._requester.request("post", url, False, cast=APIApp, body=body, headers=headers)

    def update(
        self,
        *,
        app_id: str,
        name: Optional[str] = None,
        callback_url: Optional[str] = None,
        **kwargs,
    ) -> UpdateAPIAppsResp:
        """
        update api app

        :param app_id: The id of the api app.
        :param name: The name of the api app, required when app_type is normal.
        :param callback_url: The callback url of the api app.
        """
        url = f"{self._base_url}/v1/api_apps/{app_id}"
        body = dump_exclude_none(
            {
                "name": name,
                "callback_url": callback_url,
            }
        )
        headers: Optional[dict] = kwargs.get("headers")

        return self._requester.request(
            "put",
            url,
            False,
            cast=UpdateAPIAppsResp,
            body=body,
            headers=headers,
        )

    def delete(self, *, app_id: str, **kwargs) -> DeleteAPIAppsResp:
        url = f"{self._base_url}/v1/api_apps/{app_id}"
        headers: Optional[dict] = kwargs.get("headers")

        return self._requester.request("delete", url, False, cast=DeleteAPIAppsResp, headers=headers)

    def list(
        self, *, app_type: Optional[AppType] = None, page_token: str = "", page_size: int = 20, **kwargs
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

            self._events = AsyncAPIAppsEventsClient(self._base_url, self._requester)
        return self._events

    async def create(
        self,
        *,
        app_type: AppType,
        name: Optional[str] = None,
        connector_id: Optional[str] = None,
        **kwargs,
    ) -> APIApp:
        """create api app

        :param app_type: The type of the api app.
        :param name: The name of the api app, required when app_type is normal.
        :param connector_id: The connector id of the api app, required when app_type is connector.
        :return: The api app object.
        """
        url = f"{self._base_url}/v1/api_apps"
        body = dump_exclude_none(
            {
                "app_type": app_type,
                "name": name,
                "connector_id": connector_id,
            }
        )
        headers: Optional[dict] = kwargs.get("headers")

        return await self._requester.arequest("post", url, False, cast=APIApp, body=body, headers=headers)

    async def update(
        self,
        *,
        app_id: str,
        name: Optional[str] = None,
        callback_url: Optional[str] = None,
        **kwargs,
    ) -> UpdateAPIAppsResp:
        """
        update api app

        :param app_id: The id of the api app.
        :param name: The name of the api app, required when app_type is normal.
        :param callback_url: The callback url of the api app.
        """
        url = f"{self._base_url}/v1/api_apps/{app_id}"
        body = dump_exclude_none(
            {
                "name": name,
                "callback_url": callback_url,
            }
        )
        headers: Optional[dict] = kwargs.get("headers")

        return await self._requester.arequest(
            "put",
            url,
            False,
            cast=UpdateAPIAppsResp,
            body=body,
            headers=headers,
        )

    async def delete(self, *, app_id: str, **kwargs) -> DeleteAPIAppsResp:
        url = f"{self._base_url}/v1/api_apps/{app_id}"
        headers: Optional[dict] = kwargs.get("headers")

        return await self._requester.arequest("delete", url, False, cast=DeleteAPIAppsResp, headers=headers)

    async def list(
        self, *, app_type: Optional[AppType] = None, page_token: str = "", page_size: int = 20, **kwargs
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
