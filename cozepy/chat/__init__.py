from enum import Enum

from cozepy.auth import Auth
from cozepy.request import Requester


class ChatClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester
        self._v3 = None

    @property
    def v3(self):
        if not self._v3:
            from .v3 import ChatClient

            self._v3 = ChatClient(self._base_url, self._auth, self._requester)
        return self._v3
