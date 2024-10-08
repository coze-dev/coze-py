from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import httpx
from httpx import Response
from pydantic import BaseModel
from typing_extensions import get_args, get_origin

from cozepy.config import DEFAULT_CONNECTION_LIMITS, DEFAULT_TIMEOUT
from cozepy.exception import CozeAPIError, CozePKCEAuthError
from cozepy.log import log_debug, log_warning
from cozepy.version import user_agent

if TYPE_CHECKING:
    from cozepy.auth import Auth

T = TypeVar("T", bound=BaseModel)


class HTTPClient(httpx.Client):
    def __init__(self, **kwargs):
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        kwargs.setdefault("limits", DEFAULT_CONNECTION_LIMITS)
        kwargs.setdefault("follow_redirects", True)
        super().__init__(**kwargs)


class Requester(object):
    """
    http request helper class.
    """

    def __init__(self, auth: "Auth" = None, client: HTTPClient = None):
        self._auth = auth
        if client is None:
            client = HTTPClient()
        self._client = client

    def request(
        self,
        method: str,
        url: str,
        model: Union[Type[T], Iterable[Type[T]], None],
        params: dict = None,
        headers: dict = None,
        body: dict = None,
        files: dict = None,
        stream: bool = False,
        data_field: str = "data",
    ) -> Union[T, List[T], Tuple[Iterator[str], str], None]:
        """
        Send a request to the server.
        """
        method = method.upper()
        request = self._make_request(
            method,
            url,
            params=params,
            headers=headers,
            json=body,
            files=files,
        )
        log_debug("request %s#%s sending, params=%s, json=%s, stream=%s", method, url, params, body, stream)
        response = self._client.send(request, stream=stream)
        logid = response.headers.get("x-tt-logid")
        if stream:
            return response.iter_lines(), logid

        code, msg, data = self._parse_requests_code_msg(method, url, response, data_field)

        if code is not None and code > 0:
            log_warning("request %s#%s failed, logid=%s, code=%s, msg=%s", method, url, logid, code, msg)
            raise CozeAPIError(code, msg, logid)
        elif code is None and msg != "":
            log_warning("request %s#%s failed, logid=%s, msg=%s", method, url, logid, msg)
            if msg in ["authorization_pending", "slow_down", "access_denied", "expired_token"]:
                raise CozePKCEAuthError(msg, logid)
            raise CozeAPIError(code, msg, logid)
        if get_origin(model) is list:
            item_model = get_args(model)[0]
            return [item_model.model_validate(item) for item in data]
        else:
            if model is None:
                return None
            return model.model_validate(data)

    def _make_request(
        self,
        method: str,
        url: str,
        params: dict = None,
        headers: dict = None,
        json: dict = None,
        files: dict = None,
    ) -> httpx.Request:
        if headers is None:
            headers = {}
        headers["User-Agent"] = user_agent()
        if self._auth:
            self._auth.authentication(headers)
        return httpx.Request(
            method,
            url,
            params=params,
            headers=headers,
            json=json,
            files=files,
        )

    def _parse_requests_code_msg(
        self, method: str, url: str, response: Response, data_field: str = "data"
    ) -> Tuple[Optional[int], str, Any]:
        try:
            body = response.json()
            logid = response.headers.get("x-tt-logid")
            log_debug("request %s#%s responding, logid=%s, data=%s", method, url, logid, body)
        except Exception as e:  # noqa: E722
            raise CozeAPIError(
                response.status_code,
                response.text,
                response.headers.get("x-tt-logid"),
            ) from e

        if "code" in body and "msg" in body and int(body["code"]) > 0:
            return int(body["code"]), body["msg"], body.get(data_field)
        if "error_code" in body and body["error_code"] in [
            "authorization_pending",
            "slow_down",
            "access_denied",
            "expired_token",
        ]:
            return None, body["error_code"], None
        if "error_message" in body and body["error_message"] != "":
            return None, body["error_message"], None
        if data_field in body:
            if "first_id" in body:
                return (
                    0,
                    "",
                    {
                        "first_id": body["first_id"],
                        "has_more": body["has_more"],
                        "last_id": body["last_id"],
                        "items": body["data"],
                    },
                )
            if "debug_url" in body:
                return (
                    0,
                    "",
                    {
                        "data": body[data_field],
                        "debug_url": body["debug_url"],
                    },
                )
            return 0, "", body[data_field]
        return 0, "", body
