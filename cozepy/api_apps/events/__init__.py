from typing import List, Optional

from cozepy.model import AsyncTokenPaged, CozeModel, HTTPRequest, TokenPaged, TokenPagedResponse
from cozepy.request import Requester
from cozepy.util import dump_exclude_none, remove_none_values, remove_url_trailing_slash


class APIAppEvent(CozeModel):
    api_app_id: str
    name: str
    description: str
    event_type: str


class CreateAPIAppsEventsResp(CozeModel):
    pass


class UpdateAPIAppsEventsResp(CozeModel):
    pass


class DeleteAPIAppsEventsResp(CozeModel):
    pass


class _PrivateListAPIAppsEventsData(CozeModel, TokenPagedResponse[APIAppEvent]):
    items: List[APIAppEvent]
    next_page_token: Optional[str] = None
    has_more: bool

    def get_next_page_token(self) -> Optional[str]:
        return self.next_page_token

    def get_has_more(self) -> Optional[bool]:
        return self.has_more

    def get_items(self) -> List[APIAppEvent]:
        return self.items


class APIAppsEventsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(
        self,
        *,
        api_app_id: str,
        event_types: List[str],
        **kwargs,
    ) -> CreateAPIAppsEventsResp:
        url = f"{self._base_url}/v1/api_apps/{api_app_id}/events"
        body = dump_exclude_none(
            {
                "event_types": event_types,
            }
        )
        headers: Optional[dict] = kwargs.get("headers")

        return self._requester.request("post", url, False, cast=CreateAPIAppsEventsResp, body=body, headers=headers)

    def delete(self, *, api_app_id: str, event_types: List[str], **kwargs) -> DeleteAPIAppsEventsResp:
        url = f"{self._base_url}/v1/api_apps/{api_app_id}/events"
        body = dump_exclude_none(
            {
                "event_types": event_types,
            }
        )
        headers: Optional[dict] = kwargs.get("headers")

        return self._requester.request("delete", url, False, cast=DeleteAPIAppsEventsResp, body=body, headers=headers)

    def list(self, *, api_app_id: str, page_token: str = "", page_size: int = 20, **kwargs) -> TokenPaged[APIAppEvent]:
        url = f"{self._base_url}/v1/api_apps/{api_app_id}/events"
        headers: Optional[dict] = kwargs.get("headers")

        def request_maker(i_page_token: str, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                params=remove_none_values(
                    {
                        "page_size": i_page_size,
                        "page_token": i_page_token,
                    }
                ),
                cast=_PrivateListAPIAppsEventsData,
                headers=headers,
                stream=False,
            )

        return TokenPaged(
            page_token=page_token,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )


class AsyncAPIAppsEventsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def create(
        self,
        *,
        api_app_id: str,
        event_types: List[str],
        **kwargs,
    ) -> CreateAPIAppsEventsResp:
        url = f"{self._base_url}/v1/api_apps/{api_app_id}/events"
        body = dump_exclude_none(
            {
                "event_types": event_types,
            }
        )
        headers: Optional[dict] = kwargs.get("headers")

        return await self._requester.arequest(
            "post", url, False, cast=CreateAPIAppsEventsResp, body=body, headers=headers
        )

    async def delete(self, *, api_app_id: str, event_types: List[str], **kwargs) -> DeleteAPIAppsEventsResp:
        url = f"{self._base_url}/v1/api_apps/{api_app_id}/events"
        body = dump_exclude_none(
            {
                "event_types": event_types,
            }
        )
        headers: Optional[dict] = kwargs.get("headers")

        return await self._requester.arequest(
            "delete", url, False, cast=DeleteAPIAppsEventsResp, body=body, headers=headers
        )

    async def list(
        self, *, api_app_id: str, page_token: str = "", page_size: int = 20, **kwargs
    ) -> AsyncTokenPaged[APIAppEvent]:
        url = f"{self._base_url}/v1/api_apps/{api_app_id}/events"
        headers: Optional[dict] = kwargs.get("headers")

        async def request_maker(i_page_token: str, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "GET",
                url,
                params=remove_none_values(
                    {
                        "page_size": i_page_size,
                        "page_token": i_page_token,
                    }
                ),
                cast=_PrivateListAPIAppsEventsData,
                headers=headers,
                stream=False,
            )

        return await AsyncTokenPaged.build(
            page_token=page_token,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )
