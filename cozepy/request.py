from typing import TYPE_CHECKING, Tuple, Optional

import requests
from requests import Response

if TYPE_CHECKING:
    from cozepy.auth import Auth

from typing import Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def json_obj_to_pydantic(json_obj: dict, model: Type[T]) -> T:
    """
    将 JSON 字符串转换为指定的 Pydantic 模型对象。
    """
    return model.model_validate(json_obj)


class Requester(object):
    """
    http request helper class.
    """

    def __init__(self, auth: "Auth" = None):
        self._auth = auth

    def request(
        self,
        method: str,
        url: str,
        model: Type[T],
        params: dict = None,
        headers: dict = None,
        body: dict = None,
    ) -> T:
        """
        Send a request to the server.
        """
        if headers is None:
            headers = {}
        if self._auth:
            self._auth.authentication(headers)
        r = requests.request(method, url, params=params, headers=headers, json=body)

        code, msg, data = self.__parse_requests_code_msg(r)

        if code is not None and code > 0:
            # TODO: Exception 自定义类型
            logid = r.headers.get("x-tt-logid")
            raise Exception(f"{code}: {msg}, logid:{logid}")
        elif code is None and msg != "":
            logid = r.headers.get("x-tt-logid")
            raise Exception(f"{msg}, logid:{logid}")
        return model.model_validate(data)

    async def arequest(self, method: str, path: str, **kwargs) -> dict:
        """
        Send a request to the server with asyncio.
        """
        pass

    def __parse_requests_code_msg(self, r: Response) -> Tuple[Optional[int], str, Optional[T]]:
        try:
            json = r.json()
        except:
            r.raise_for_status()
            return

        if "code" in json and "msg" in json and int(json["code"]) > 0:
            return int(json["code"]), json["msg"], json["data"]
        if "error_message" in json and json["error_message"] != "":
            return None, json["error_message"], None
        if "data" in json:
            return 0, "", json["data"]
        return 0, "", json
