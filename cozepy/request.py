from typing import TYPE_CHECKING, Tuple, Optional, Union, List, Iterator, Type, TypeVar
from pydantic import BaseModel
import httpx
from httpx import Response
from typing_extensions import get_args, get_origin  # compatibility with python 3.7

from cozepy.version import user_agent
from cozepy.exception import CozeAPIError

if TYPE_CHECKING:
    from cozepy.auth import Auth


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
        model: Union[Type[T], List[Type[T]]],
        params: dict = None,
        headers: dict = None,
        body: dict = None,
        files: dict = None,
        stream: bool = False,
        data_field: str = "data",
    ) -> Union[T, List[T], Iterator[str]]:
        """
        Send a request to the server.
        """
        if headers is None:
            headers = {}
        headers["User-Agent"] = user_agent()
        if self._auth:
            self._auth.authentication(headers)
        r = httpx.request(
            method,
            url,
            params=params,
            headers=headers,
            json=body,
            files=files,
        )
        logid = r.headers.get("x-tt-logid")
        if stream:
            return r.iter_lines()

        code, msg, data = self._parse_requests_code_msg(r, data_field)

        if code is not None and code > 0:
            raise CozeAPIError(code, msg, logid)
        elif code is None and msg != "":
            raise CozeAPIError(code, msg, logid)
        if get_origin(model) is list:
            item_model = get_args(model)[0]
            return [item_model.model_validate(item) for item in data]
        else:
            if model is None:
                return None
            return model.model_validate(data)

    async def arequest(self, method: str, path: str, **kwargs) -> dict:
        """
        Send a request to the server with asyncio.
        """
        pass

    def _parse_requests_code_msg(
        self, r: Response, data_field: str = "data"
    ) -> Tuple[Optional[int], str, Optional[T]]:
        try:
            json = r.json()
        except:  # noqa: E722
            r.raise_for_status()
            return

        if "code" in json and "msg" in json and int(json["code"]) > 0:
            return int(json["code"]), json["msg"], json.get(data_field) or None
        if "error_message" in json and json["error_message"] != "":
            return None, json["error_message"], None
        if data_field in json:
            if "first_id" in json:
                return (
                    0,
                    "",
                    {
                        "first_id": json["first_id"],
                        "has_more": json["has_more"],
                        "last_id": json["last_id"],
                        "items": json["data"],
                    },
                )
            if "debug_url" in json:
                return (
                    0,
                    "",
                    {
                        "data": json[data_field],
                        "debug_url": json["debug_url"],
                    },
                )
            return 0, "", json[data_field]
        return 0, "", json
