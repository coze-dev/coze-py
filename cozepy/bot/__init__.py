from typing import TYPE_CHECKING

from cozepy.auth import Auth
from cozepy.request import Requester

if TYPE_CHECKING:
    from .v1 import BotClient as BotClientV1


class BotClient(object):
    """
    Bot class.
    """

    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester
        self._v1 = None

    @property
    def v1(self) -> "BotClientV1":
        if not self._v1:
            from .v1 import BotClient

            self._v1 = BotClient(self._base_url, self._auth, self._requester)
        return self._v1
