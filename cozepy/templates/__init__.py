from enum import Enum
from typing import Optional

from cozepy.auth import Auth
from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


class TemplateEntityType(str, Enum):
    AGENT = "agent"


class TemplateDuplicateResp(CozeModel):
    entity_id: str
    entity_type: TemplateEntityType


class TemplatesClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._auth = auth
        self._requester = requester

    def duplicate(
        self, *, template_id: str, workspace_id: str, name: Optional[str] = None, **kwargs
    ) -> TemplateDuplicateResp:
        url = f"{self._base_url}/v1/templates/{template_id}/duplicate"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "workspace_id": workspace_id,
            "name": name,
        }
        return self._requester.request("post", url, False, TemplateDuplicateResp, headers=headers, body=body)


class AsyncTemplatesClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._auth = auth
        self._requester = requester

    async def duplicate(
        self, *, template_id: str, workspace_id: str, name: Optional[str] = None, **kwargs
    ) -> TemplateDuplicateResp:
        url = f"{self._base_url}/v1/templates/{template_id}/duplicate"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "workspace_id": workspace_id,
            "name": name,
        }
        return await self._requester.arequest("post", url, False, TemplateDuplicateResp, headers=headers, body=body)
