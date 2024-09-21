from typing import TYPE_CHECKING, Optional

import requests

if TYPE_CHECKING:
    from cozepy.auth import Auth

from typing import Type, TypeVar

from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


def json_obj_to_pydantic(json_obj: dict, model: Type[T]) -> T:
    """
    将 JSON 字符串转换为指定的 Pydantic 模型对象。
    """
    return model.model_validate(json_obj)


class Requester(object):
    """
    http request helper class.
    """

    def __init__(self,
                 auth: Optional["Auth"]
                 ):
        self._auth = auth

    def request(self, method: str, url: str, model: Type[T], params: dict = None, headers: dict = None) -> T:
        """
        Send a request to the server.
        """
        if headers is None:
            headers = {}
        self._auth.authentication(headers)
        r = requests.request(method, url, params=params, headers=headers)
        logid = r.headers.get('x-tt-logid')

        try:
            json = r.json()
            code = json.get('code') or 0
            msg = json.get('msg') or ''
            data = json.get('data')
        except:
            r.raise_for_status()

            code = 0
            msg = ''
            data = {}

        if code > 0:
            # TODO: Exception 自定义类型
            raise Exception(f'{code}: {msg}, logid:{logid}')
        return model.model_validate(data)

    async def arequest(self, method: str, path: str, **kwargs) -> dict:
        """
        Send a request to the server with asyncio.
        """
        pass
