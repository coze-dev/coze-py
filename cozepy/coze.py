from typing import TYPE_CHECKING

from cozepy.auth import Auth
from cozepy.request import Requester

if TYPE_CHECKING:
    from cozepy.bot import BotClient


class Coze(object):
    def __init__(self,
                 auth: Auth,
                 base_url: str = 'https://api.coze.com',
                 ):
        self._auth = auth
        self._base_url = base_url
        self._requester = Requester(auth=auth)

        # service client
        self._bot = None

    @property
    def bot(self) -> 'BotClient':
        if not self._bot:
            from cozepy.bot import BotClient
            self._bot = BotClient(self._base_url, self._auth, self._requester)
        return self._bot
