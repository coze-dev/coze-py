from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

import httpx
from httpx import Response
from pydantic import BaseModel
from typing_extensions import Literal

from cozepy.config import DEFAULT_CONNECTION_LIMITS, DEFAULT_TIMEOUT
from cozepy.exception import COZE_PKCE_AUTH_ERROR_TYPE_ENUMS, CozeAPIError, CozePKCEAuthError, CozePKCEAuthErrorType
from cozepy.log import log_debug, log_warning
from cozepy.model import HTTPRequest
from cozepy.version import user_agent

if TYPE_CHECKING:
    from cozepy.auth import Auth

T = TypeVar("T", bound=BaseModel)


class SyncHTTPClient(httpx.Client):
    def __init__(self, **kwargs):
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        kwargs.setdefault("limits", DEFAULT_CONNECTION_LIMITS)
        kwargs.setdefault("follow_redirects", True)
        super().__init__(**kwargs)


class AsyncHTTPClient(httpx.AsyncClient):
    def __init__(self, **kwargs):
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        kwargs.setdefault("limits", DEFAULT_CONNECTION_LIMITS)
        kwargs.setdefault("follow_redirects", True)
        super().__init__(**kwargs)


class Requester(object):
    """
    http request helper class.
    """

    def __init__(
        self,
        auth: Optional["Auth"] = None,
        sync_client: Optional[SyncHTTPClient] = None,
        async_client: Optional[AsyncHTTPClient] = None,
    ):
        self._auth = auth
        self._sync_client = sync_client
        self._async_client = async_client

    def make_request(
        self,
        method: str,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        json: Optional[dict] = None,
        files: Optional[dict] = None,
        cast: Union[Type[T], List[Type[T]], None] = None,
        data_field: str = "data",
        is_async: Optional[bool] = None,
        stream: bool = False,
    ) -> HTTPRequest:
        if headers is None:
            headers = {}
        headers["User-Agent"] = user_agent()
        if self._auth:
            self._auth.authentication(headers)

        log_debug(
            "request %s#%s sending, params=%s, json=%s, stream=%s, async=%s",
            method,
            url,
            params,
            json,
            stream,
            is_async,
        )

        return HTTPRequest(
            method=method,
            url=url,
            params=params,
            headers=headers,
            json_body=json,
            files=files,
            is_async=is_async,
            stream=stream,
            data_field=data_field,
            cast=cast,
        )

    @overload
    def request(
        self,
        method: str,
        url: str,
        stream: Literal[False],
        model: Type[T],
        params: dict = ...,
        headers: dict = ...,
        body: dict = ...,
        files: dict = ...,
        data_field: str = ...,
    ) -> T: ...

    @overload
    def request(
        self,
        method: str,
        url: str,
        stream: Literal[False],
        model: List[Type[T]],
        params: dict = ...,
        headers: dict = ...,
        body: dict = ...,
        files: dict = ...,
        data_field: str = ...,
    ) -> List[T]: ...

    @overload
    def request(
        self,
        method: str,
        url: str,
        stream: Literal[True],
        model: None,
        params: dict = ...,
        headers: dict = ...,
        body: dict = ...,
        files: dict = ...,
        data_field: str = ...,
    ) -> Tuple[Iterator[str], str]: ...

    @overload
    def request(
        self,
        method: str,
        url: str,
        stream: Literal[False],
        model: None,
        params: dict = ...,
        headers: dict = ...,
        body: dict = ...,
        files: dict = ...,
        data_field: str = ...,
    ) -> None: ...

    def request(
        self,
        method: str,
        url: str,
        stream: Literal[True, False],
        model: Union[Type[T], List[Type[T]], None],
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        body: Optional[dict] = None,
        files: Optional[dict] = None,
        data_field: str = "data",
    ) -> Union[T, List[T], Tuple[Iterator[str], str], None]:
        """
        Send a request to the server.
        """
        method = method.upper()

        request = self.make_request(
            method,
            url,
            params=params,
            headers=headers,
            json=body,
            files=files,
            cast=model,
            data_field=data_field,
            stream=stream,
            is_async=False,
        )

        return self.send(request)

    def send(
        self,
        request: HTTPRequest,
    ) -> Union[T, List[T], Tuple[Iterator[str], str], None]:
        """
        Send a request to the server.
        """
        return self._parse_response(
            method=request.method,
            url=request.url,
            is_async=False,
            response=self.sync_client.send(request.as_httpx, stream=False),
            model=request.cast,
            stream=request.stream,
            data_field=request.data_field,
        )

    @overload
    async def arequest(
        self,
        method: str,
        url: str,
        stream: Literal[False],
        model: Type[T],
        params: dict = ...,
        headers: dict = ...,
        body: dict = ...,
        files: dict = ...,
        data_field: str = ...,
    ) -> T: ...

    @overload
    async def arequest(
        self,
        method: str,
        url: str,
        stream: Literal[False],
        model: List[Type[T]],
        params: dict = ...,
        headers: dict = ...,
        body: dict = ...,
        files: dict = ...,
        data_field: str = ...,
    ) -> List[T]: ...

    @overload
    async def arequest(
        self,
        method: str,
        url: str,
        stream: Literal[False],
        model: None,
        params: Optional[dict] = ...,
        headers: Optional[dict] = ...,
        body: Optional[dict] = ...,
        files: Optional[dict] = ...,
        data_field: str = ...,
    ) -> None: ...

    @overload
    async def arequest(
        self,
        method: str,
        url: str,
        stream: Literal[True],
        model: None,
        params: Optional[dict] = ...,
        headers: Optional[dict] = ...,
        body: Optional[dict] = ...,
        files: Optional[dict] = ...,
        data_field: str = ...,
    ) -> Tuple[AsyncIterator[str], str]: ...

    async def arequest(
        self,
        method: str,
        url: str,
        stream: Literal[True, False],
        model: Union[Type[T], List[Type[T]], None],
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        body: Optional[dict] = None,
        files: Optional[dict] = None,
        data_field: str = "data",
    ) -> Union[T, List[T], Tuple[AsyncIterator[str], str], None]:
        """
        Send a request to the server.
        """
        method = method.upper()
        request = self.make_request(
            method, url, params=params, headers=headers, json=body, files=files, stream=stream, is_async=True
        )

        response = await self.async_client.send(request.as_httpx, stream=stream)
        return self._parse_response(
            method, url, True, response=response, model=model, stream=stream, data_field=data_field
        )

    async def asend(
        self,
        request: HTTPRequest,
    ) -> Union[T, List[T], Tuple[AsyncIterator[str], str], None]:
        return self._parse_response(
            method=request.method,
            url=request.url,
            is_async=True,
            response=await self.async_client.send(request.as_httpx, stream=request.stream),
            model=request.cast,
            stream=request.stream,
            data_field=request.data_field,
        )

    @property
    def sync_client(self) -> "SyncHTTPClient":
        if self._sync_client is None:
            self._sync_client = SyncHTTPClient()
        return self._sync_client

    @property
    def async_client(self) -> "AsyncHTTPClient":
        if self._async_client is None:
            self._async_client = AsyncHTTPClient()
        return self._async_client

    @overload
    def _parse_response(
        self,
        method: str,
        url: str,
        is_async: Literal[False],
        response: httpx.Response,
        model: Union[Type[T], List[Type[T]], None],
        stream: bool = ...,
        data_field: str = ...,
    ) -> Union[T, List[T], Tuple[Iterator[str], str], None]: ...

    @overload
    def _parse_response(
        self,
        method: str,
        url: str,
        is_async: Literal[True],
        response: httpx.Response,
        model: Union[Type[T], List[Type[T]], None],
        stream: bool = ...,
        data_field: str = ...,
    ) -> Union[T, List[T], Tuple[AsyncIterator[str], str], None]: ...

    def _parse_response(
        self,
        method: str,
        url: str,
        is_async: Literal[True, False],
        response: httpx.Response,
        model: Union[Type[T], List[Type[T]], None],
        stream: bool = False,
        data_field: str = "data",
    ) -> Union[T, List[T], Tuple[Iterator[str], str], Tuple[AsyncIterator[str], str], None]:
        logid = response.headers.get("x-tt-logid")
        if stream:
            if is_async:
                return response.aiter_lines(), logid
            return response.iter_lines(), logid

        code, msg, data = self._parse_requests_code_msg(method, url, response, data_field)

        if code is not None and code > 0:
            log_warning("request %s#%s failed, logid=%s, code=%s, msg=%s", method, url, logid, code, msg)
            raise CozeAPIError(code, msg, logid)
        elif code is None and msg != "":
            log_warning("request %s#%s failed, logid=%s, msg=%s", method, url, logid, msg)
            if msg in COZE_PKCE_AUTH_ERROR_TYPE_ENUMS:
                raise CozePKCEAuthError(CozePKCEAuthErrorType(msg), logid)
            raise CozeAPIError(code, msg, logid)
        if isinstance(model, List):
            item_model = model[0]
            return [item_model.model_validate(item) for item in data]
        else:
            if model is None:
                return None
            return model.model_validate(data)

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
        if "error_code" in body and body["error_code"] in COZE_PKCE_AUTH_ERROR_TYPE_ENUMS:
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
