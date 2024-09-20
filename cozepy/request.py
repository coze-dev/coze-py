from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from cozepy.auth import Auth


class Requester(object):
    """
    http request helper class.
    """

    def __init__(self,
                 auth: Optional["Auth"]
                 ):
        self._auth = auth

    def request(self, method: str, path: str, **kwargs) -> dict:
        """
        Send a request to the server.
        """
        pass

    async def arequest(self, method: str, path: str, **kwargs) -> dict:
        """
        Send a request to the server with asyncio.
        """
        pass
