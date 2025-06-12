from typing import List, Optional

from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


class CreateAPIAppsEventsResp(CozeModel):
    pass


class UpdateAPIAppsEventsResp(CozeModel):
    pass


class DeleteAPIAppsEventsResp(CozeModel):
    pass


class APIAppsEventsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(
        self,
        *,
        app_id: str,
        event_types: List[str],
        **kwargs,
    ) -> CreateAPIAppsEventsResp:
        url = f"{self._base_url}/v1/api_apps/{app_id}/events"
        body = {
            "event_types": event_types,
        }
        headers: Optional[dict] = kwargs.get("headers")

        return self._requester.request("post", url, False, cast=CreateAPIAppsEventsResp, body=body, headers=headers)

    def delete(self, *, app_id: str, event_types: List[str], **kwargs) -> DeleteAPIAppsEventsResp:
        url = f"{self._base_url}/v1/api_apps/{app_id}/events"
        body = {
            "event_types": event_types,
        }
        headers: Optional[dict] = kwargs.get("headers")

        return self._requester.request("delete", url, False, cast=DeleteAPIAppsEventsResp, body=body, headers=headers)
