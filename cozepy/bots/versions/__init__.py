from typing import List, Optional

from cozepy.bots import PublishStatus
from cozepy.model import AsyncNumberPaged, CozeModel, NumberPaged, NumberPagedResponse
from cozepy.request import HTTPRequest, Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash


class BotVersionUserInfo(CozeModel):
    id: str
    name: str


class BotVersionInfo(CozeModel):
    version: str
    description: str
    created_at: str
    updated_at: str
    creator: BotVersionUserInfo


class _PrivateListBotVersionsData(CozeModel, NumberPagedResponse[BotVersionInfo]):
    items: List[BotVersionInfo]
    total: int

    def get_total(self) -> Optional[int]:
        return self.total

    def get_has_more(self) -> Optional[bool]:
        return None

    def get_items(self) -> List[BotVersionInfo]:
        return self.items


class BotsVersionsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def list(
        self,
        *,
        bot_id: str,
        publish_status: Optional[PublishStatus] = None,
        connector_id: Optional[str] = None,
        page_num: int = 1,
        page_size: int = 10,
        **kwargs,
    ) -> NumberPaged[BotVersionInfo]:
        url = f"{self._base_url}/v1/bots/{bot_id}/versions"
        headers: Optional[dict] = kwargs.get("headers")

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                headers=headers,
                params=remove_none_values(
                    {
                        "page_num": i_page_num,
                        "page_size": i_page_size,
                        "publish_status": publish_status.value if publish_status else None,
                        "connector_id": connector_id,
                    }
                ),
                cast=_PrivateListBotVersionsData,
                stream=False,
            )

        return NumberPaged(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )


class AsyncBotsVersionsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def list(
        self,
        *,
        bot_id: str,
        publish_status: Optional[PublishStatus] = None,
        connector_id: Optional[str] = None,
        page_num: int = 1,
        page_size: int = 10,
        **kwargs,
    ) -> AsyncNumberPaged[BotVersionInfo]:
        url = f"{self._base_url}/v1/bots/{bot_id}/versions"
        headers: Optional[dict] = kwargs.get("headers")

        async def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "GET",
                url,
                headers=headers,
                params=remove_none_values(
                    {
                        "page_num": i_page_num,
                        "page_size": i_page_size,
                        "publish_status": publish_status.value if publish_status else None,
                        "connector_id": connector_id,
                    }
                ),
                cast=_PrivateListBotVersionsData,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )
