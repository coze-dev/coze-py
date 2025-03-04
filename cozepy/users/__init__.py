from typing import Optional

from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


class User(CozeModel):
    user_id: str
    user_name: str
    nick_name: str
    avatar_url: str


class UsersClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def me(self, **kwargs) -> User:
        url = f"{self._base_url}/v1/users/me"
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("get", url, False, User, headers=headers)


class AsyncUsersClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def me(self, **kwargs) -> User:
        url = f"{self._base_url}/v1/users/me"
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest("get", url, False, User, headers=headers)
