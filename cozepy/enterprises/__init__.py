from typing import TYPE_CHECKING, Optional

from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash

if TYPE_CHECKING:
    from .members import AsyncEnterprisesMembersClient, EnterprisesMembersClient


class EnterprisesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

        self._members: Optional[EnterprisesMembersClient] = None

    @property
    def members(self) -> "EnterprisesMembersClient":
        if not self._members:
            from .members import EnterprisesMembersClient

            self._members = EnterprisesMembersClient(self._base_url, self._requester)
        return self._members


class AsyncEnterprisesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

        self._members: Optional[AsyncEnterprisesMembersClient] = None

    @property
    def members(self) -> "AsyncEnterprisesMembersClient":
        if not self._members:
            from .members import AsyncEnterprisesMembersClient

            self._members = AsyncEnterprisesMembersClient(self._base_url, self._requester)
        return self._members
