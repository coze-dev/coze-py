from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


class ConnectorsClient(object):
    """
    渠道客户端

    提供渠道相关功能的客户端类。
    """

    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._bots = None

    @property
    def bots(self):
        """
        渠道Bot客户端
        """
        if not self._bots:
            from .bots import ConnectorsBotsClient

            self._bots = ConnectorsBotsClient(self._base_url, self._requester)
        return self._bots


class AsyncConnectorsClient(object):
    """
    异步渠道客户端

    提供异步渠道相关功能的客户端类。
    """

    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester
        self._bots = None

    @property
    def bots(self):
        """
        异步渠道Bot客户端
        """
        if not self._bots:
            from .bots import AsyncConnectorsBotsClient

            self._bots = AsyncConnectorsBotsClient(self._base_url, self._requester)
        return self._bots
