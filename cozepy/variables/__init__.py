from typing import List, Optional

from cozepy.model import CozeModel, ListResponse
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash


class VariableValue(CozeModel):
    keyword: str
    value: str
    create_time: int = 0
    update_time: int = 0


class _PrivateVariablesRetrieveData(CozeModel):
    items: List[VariableValue]


class UpdateVariableResp(CozeModel):
    pass


class VariablesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def retrieve(
        self,
        *,
        connector_uid: str,
        keywords: List[str],
        app_id: Optional[str] = None,
        bot_id: Optional[str] = None,
        connector_id: Optional[str] = None,
    ) -> ListResponse[VariableValue]:
        url = f"{self._base_url}/v1/variables"
        params = remove_none_values(
            {
                "app_id": app_id,
                "bot_id": bot_id,
                "connector_id": connector_id,
                "connector_uid": connector_uid,
                "keywords": ",".join(keywords),
            }
        )
        res = self._requester.request("get", url, False, _PrivateVariablesRetrieveData, params=params)
        return ListResponse[VariableValue](raw_response=res.response._raw_response, data=res.items)

    def update(
        self,
        *,
        connector_uid: str,
        data: List[VariableValue],
        app_id: Optional[str] = None,
        bot_id: Optional[str] = None,
        connector_id: Optional[str] = None,
    ) -> UpdateVariableResp:
        url = f"{self._base_url}/v1/variables"
        body = remove_none_values(
            {
                "app_id": app_id,
                "bot_id": bot_id,
                "connector_id": connector_id,
                "connector_uid": connector_uid,
                "data": [
                    {
                        "keyword": v.keyword,
                        "value": v.value,
                    }
                    for v in data
                ],
            }
        )
        return self._requester.request(
            "put",
            url,
            False,
            cast=UpdateVariableResp,
            body=body,
        )


class AsyncVariablesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def retrieve(
        self,
        *,
        connector_uid: str,
        keywords: List[str],
        app_id: Optional[str] = None,
        bot_id: Optional[str] = None,
        connector_id: Optional[str] = None,
    ) -> ListResponse[VariableValue]:
        url = f"{self._base_url}/v1/variables"
        params = remove_none_values(
            {
                "app_id": app_id,
                "bot_id": bot_id,
                "connector_id": connector_id,
                "connector_uid": connector_uid,
                "keywords": ",".join(keywords),
            }
        )
        res = await self._requester.arequest("get", url, False, _PrivateVariablesRetrieveData, params=params)
        return ListResponse[VariableValue](raw_response=res.response._raw_response, data=res.items)

    async def update(
        self,
        *,
        connector_uid: str,
        data: List[VariableValue],
        app_id: Optional[str] = None,
        bot_id: Optional[str] = None,
        connector_id: Optional[str] = None,
    ) -> UpdateVariableResp:
        url = f"{self._base_url}/v1/variables"
        body = remove_none_values(
            {
                "app_id": app_id,
                "bot_id": bot_id,
                "connector_id": connector_id,
                "connector_uid": connector_uid,
                "data": [
                    {
                        "keyword": v.keyword,
                        "value": v.value,
                    }
                    for v in data
                ],
            }
        )
        return await self._requester.arequest(
            "put",
            url,
            False,
            cast=UpdateVariableResp,
            body=body,
        )
