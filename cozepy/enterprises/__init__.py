from typing import TYPE_CHECKING, Optional

from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash

if TYPE_CHECKING:
    from cozepy.enterprises.members import AsyncEnterprisesMembersClient, EnterprisesMembersClient
    from cozepy.enterprises.organizations import AsyncEnterprisesOrganizationsClient, EnterprisesOrganizationsClient


class EnterprisesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._members: Optional[EnterprisesMembersClient] = None
        self._organizations: Optional[EnterprisesOrganizationsClient] = None

    @property
    def members(self) -> "EnterprisesMembersClient":
        if not self._members:
            from .members import EnterprisesMembersClient

            self._members = EnterprisesMembersClient(base_url=self._base_url, requester=self._requester)
        return self._members

    @property
    def organizations(self) -> "EnterprisesOrganizationsClient":
        if not self._organizations:
            from .organizations import EnterprisesOrganizationsClient

            self._organizations = EnterprisesOrganizationsClient(base_url=self._base_url, requester=self._requester)
        return self._organizations


class AsyncEnterprisesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._members: Optional[AsyncEnterprisesMembersClient] = None
        self._organizations: Optional[AsyncEnterprisesOrganizationsClient] = None

    @property
    def members(self) -> "AsyncEnterprisesMembersClient":
        if not self._members:
            from .members import AsyncEnterprisesMembersClient

            self._members = AsyncEnterprisesMembersClient(base_url=self._base_url, requester=self._requester)
        return self._members

    @property
    def organizations(self) -> "AsyncEnterprisesOrganizationsClient":
        if not self._organizations:
            from .organizations import AsyncEnterprisesOrganizationsClient

            self._organizations = AsyncEnterprisesOrganizationsClient(
                base_url=self._base_url, requester=self._requester
            )
        return self._organizations
