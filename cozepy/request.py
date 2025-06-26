from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
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
from typing_extensions import Literal, get_args

from cozepy.config import DEFAULT_CONNECTION_LIMITS, DEFAULT_TIMEOUT
from cozepy.exception import COZE_PKCE_AUTH_ERROR_TYPE_ENUMS, CozeAPIError, CozePKCEAuthError, CozePKCEAuthErrorType
from cozepy.log import log_debug, log_warning
from cozepy.model import (
    AsyncIteratorHTTPResponse,
    FileHTTPResponse,
    HTTPRequest,
    IteratorHTTPResponse,
    ListResponse,
)
from cozepy.version import coze_client_user_agent, user_agent

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

    def auth_header(self, headers: dict):
        if self._auth:
            self._auth.authentication(headers)

    async def async_auth_header(self, headers: dict):
        if self._auth:
            await self._auth.aauthentication(headers)

    def make_request(
        self,
        method: str,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        json: Optional[dict] = None,
        files: Optional[dict] = None,
        cast: Union[Type[T], List[Type[T]], Type[ListResponse[T]], Type[FileHTTPResponse], None] = None,
        data_field: str = "data",
        stream: bool = False,
    ) -> HTTPRequest:
        if headers is None:
            headers = {}
        headers["User-Agent"] = user_agent()
        headers["X-Coze-Client-User-Agent"] = coze_client_user_agent()
        if self._auth:
            self._auth.authentication(headers)

        log_debug(
            "request %s#%s sending, params=%s, json=%s, stream=%s, async=%s",
            method,
            url,
            params,
            json,
            stream,
            False,
        )

        return HTTPRequest(
            method=method,
            url=url,
            params=params,
            headers=headers,
            json_body=json,
            files=files,
            is_async=False,
            stream=stream,
            data_field=data_field,
            cast=cast,
        )

    async def amake_request(
        self,
        method: str,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        json: Optional[dict] = None,
        files: Optional[dict] = None,
        cast: Union[Type[T], List[Type[T]], Type[ListResponse[T]], Type[FileHTTPResponse], None] = None,
        data_field: str = "data",
        stream: bool = False,
    ) -> HTTPRequest:
        if headers is None:
            headers = {}
        headers["User-Agent"] = user_agent()
        headers["X-Coze-Client-User-Agent"] = coze_client_user_agent()

        if self._auth:
            await self._auth.aauthentication(headers)

        log_debug(
            "request %s#%s sending, params=%s, json=%s, stream=%s, async=%s",
            method,
            url,
            params,
            json,
            stream,
            True,
        )

        return HTTPRequest(
            method=method,
            url=url,
            params=params,
            headers=headers,
            json_body=json,
            files=files,
            is_async=True,
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
        cast: Type[T],
        params: dict = ...,
        headers: Optional[dict] = ...,
        body: dict = ...,
        files: Optional[dict] = ...,
        data_field: str = ...,
    ) -> T: ...

    @overload
    def request(
        self,
        method: str,
        url: str,
        stream: Literal[False],
        cast: List[Type[T]],
        params: dict = ...,
        headers: Optional[dict] = ...,
        body: dict = ...,
        files: Optional[dict] = ...,
        data_field: str = ...,
    ) -> List[T]: ...

    @overload
    def request(
        self,
        method: str,
        url: str,
        stream: Literal[False],
        cast: Type[ListResponse[T]],
        params: dict = ...,
        headers: Optional[dict] = ...,
        body: dict = ...,
        files: Optional[dict] = ...,
        data_field: str = ...,
    ) -> ListResponse[T]: ...

    @overload
    def request(
        self,
        method: str,
        url: str,
        stream: Literal[False],
        cast: Type[FileHTTPResponse],
        params: dict = ...,
        headers: Optional[dict] = ...,
        body: dict = ...,
        files: Optional[dict] = ...,
        data_field: str = ...,
    ) -> FileHTTPResponse: ...

    @overload
    def request(
        self,
        method: str,
        url: str,
        stream: Literal[True],
        cast: None,
        params: dict = ...,
        headers: Optional[dict] = ...,
        body: dict = ...,
        files: Optional[dict] = ...,
        data_field: str = ...,
    ) -> IteratorHTTPResponse[str]: ...

    @overload
    def request(
        self,
        method: str,
        url: str,
        stream: Literal[False],
        cast: None,
        params: dict = ...,
        headers: Optional[dict] = ...,
        body: dict = ...,
        files: Optional[dict] = ...,
        data_field: str = ...,
    ) -> None: ...

    def request(
        self,
        method: str,
        url: str,
        stream: Literal[True, False],
        cast: Union[Type[T], List[Type[T]], Type[ListResponse[T]], Type[FileHTTPResponse], None],
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        body: Optional[dict] = None,
        files: Optional[dict] = None,
        data_field: str = "data",
    ) -> Union[T, List[T], ListResponse[T], IteratorHTTPResponse[str], FileHTTPResponse, None]:
        method = method.upper()

        request = self.make_request(
            method,
            url,
            params=params,
            headers=headers,
            json=body,
            files=files,
            cast=cast,
            data_field=data_field,
            stream=stream,
        )

        return self.send(request)

    @overload
    async def arequest(
        self,
        method: str,
        url: str,
        stream: Literal[False],
        cast: Type[T],
        params: dict = ...,
        headers: Optional[dict] = ...,
        body: dict = ...,
        files: Optional[dict] = ...,
        data_field: str = ...,
    ) -> T: ...

    @overload
    async def arequest(
        self,
        method: str,
        url: str,
        stream: Literal[False],
        cast: List[Type[T]],
        params: dict = ...,
        headers: Optional[dict] = ...,
        body: dict = ...,
        files: Optional[dict] = ...,
        data_field: str = ...,
    ) -> List[T]: ...

    @overload
    async def arequest(
        self,
        method: str,
        url: str,
        stream: Literal[False],
        cast: Type[ListResponse[T]],
        params: dict = ...,
        headers: Optional[dict] = ...,
        body: dict = ...,
        files: Optional[dict] = ...,
        data_field: str = ...,
    ) -> ListResponse[T]: ...

    @overload
    async def arequest(
        self,
        method: str,
        url: str,
        stream: Literal[False],
        cast: Type[FileHTTPResponse],
        params: dict = ...,
        headers: Optional[dict] = ...,
        body: dict = ...,
        files: Optional[dict] = ...,
        data_field: str = ...,
    ) -> FileHTTPResponse: ...

    @overload
    async def arequest(
        self,
        method: str,
        url: str,
        stream: Literal[False],
        cast: None,
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
        cast: None,
        params: Optional[dict] = ...,
        headers: Optional[dict] = ...,
        body: Optional[dict] = ...,
        files: Optional[dict] = ...,
        data_field: str = ...,
    ) -> AsyncIteratorHTTPResponse[str]: ...

    async def arequest(
        self,
        method: str,
        url: str,
        stream: Literal[True, False],
        cast: Union[Type[T], List[Type[T]], Type[ListResponse[T]], Type[FileHTTPResponse], None],
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        body: Optional[dict] = None,
        files: Optional[dict] = None,
        data_field: str = "data",
    ) -> Union[T, List[T], ListResponse[T], AsyncIteratorHTTPResponse[str], FileHTTPResponse, None]:
        method = method.upper()
        request = await self.amake_request(
            method,
            url,
            params=params,
            headers=headers,
            json=body,
            files=files,
            cast=cast,
            data_field=data_field,
            stream=stream,
        )

        return await self.asend(request)

    def send(
        self,
        request: HTTPRequest,
    ) -> Union[T, List[T], ListResponse[T], IteratorHTTPResponse[str], FileHTTPResponse, None]:
        return self._parse_response(
            method=request.method,
            url=request.url,
            response=self.sync_client.send(request.as_httpx, stream=request.stream),
            cast=request.cast,
            stream=request.stream,
            data_field=request.data_field,
        )

    async def asend(
        self,
        request: HTTPRequest,
    ) -> Union[T, List[T], ListResponse[T], AsyncIteratorHTTPResponse[str], FileHTTPResponse, None]:
        return await self._aparse_response(
            method=request.method,
            url=request.url,
            response=await self.async_client.send(request.as_httpx, stream=request.stream),
            cast=request.cast,
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

    def _parse_response(
        self,
        method: str,
        url: str,
        response: httpx.Response,
        cast: Union[Type[T], List[Type[T]], Type[ListResponse[T]], Type[FileHTTPResponse], None],
        stream: bool = False,
        data_field: str = "data",
    ) -> Union[T, List[T], ListResponse[T], IteratorHTTPResponse[str], FileHTTPResponse, None]:
        # application/json
        # text/event-stream
        # audio/<xx>
        resp_content_type = response.headers.get("content-type")
        if resp_content_type:
            resp_content_type = resp_content_type.lower()
        logid = response.headers.get("x-tt-logid")
        if stream and "event-stream" in resp_content_type:
            return IteratorHTTPResponse(response, response.iter_lines())

        if resp_content_type and "audio" in resp_content_type:
            return FileHTTPResponse(response)  # type: ignore

        code, msg, debug_url, data = self._parse_requests_code_msg(method, url, response, data_field)

        if code is not None and code > 0:
            log_warning("request %s#%s failed, logid=%s, code=%s, msg=%s", method, url, logid, code, msg)
            raise CozeAPIError(code, msg, logid, debug_url)
        elif code is None and msg != "":
            log_warning("request %s#%s failed, logid=%s, msg=%s", method, url, logid, msg)
            if msg in COZE_PKCE_AUTH_ERROR_TYPE_ENUMS:
                raise CozePKCEAuthError(CozePKCEAuthErrorType(msg), logid)
            raise CozeAPIError(code, msg, logid, debug_url)
        if isinstance(cast, List):
            item_cast = cast[0]
            return [item_cast.model_validate(item) for item in data]
        elif hasattr(cast, "__origin__") and cast.__origin__ is ListResponse:  # type: ignore
            item_cast = get_args(cast)[0]
            return ListResponse(response, [item_cast.model_validate(item) for item in data])
        else:
            if cast is None:
                return None

            res = cast.model_validate(data) if data is not None else cast()  # type: ignore
            if hasattr(res, "_raw_response"):
                res._raw_response = response  # type: ignore
            return res  # type: ignore

    async def _aparse_response(
        self,
        method: str,
        url: str,
        response: httpx.Response,
        cast: Union[Type[T], List[Type[T]], Type[ListResponse[T]], Type[FileHTTPResponse], None],
        stream: bool = False,
        data_field: str = "data",
    ) -> Union[T, List[T], ListResponse[T], AsyncIteratorHTTPResponse[str], FileHTTPResponse, None]:
        # application/json
        # text/event-stream
        # audio/<xx>
        resp_content_type = response.headers.get("content-type")
        if resp_content_type:
            resp_content_type = resp_content_type.lower()
        logid = response.headers.get("x-tt-logid")
        if stream and "event-stream" in resp_content_type:
            return AsyncIteratorHTTPResponse(response, response.aiter_lines())

        if resp_content_type and "audio" in resp_content_type:
            return FileHTTPResponse(response)  # type: ignore

        code, msg, debug_url, data = await self._aparse_requests_code_msg(method, url, response, data_field)

        if code is not None and code > 0:
            log_warning("request %s#%s failed, logid=%s, code=%s, msg=%s", method, url, logid, code, msg)
            raise CozeAPIError(code, msg, logid, debug_url)
        elif code is None and msg != "":
            log_warning("request %s#%s failed, logid=%s, msg=%s", method, url, logid, msg)
            if msg in COZE_PKCE_AUTH_ERROR_TYPE_ENUMS:
                raise CozePKCEAuthError(CozePKCEAuthErrorType(msg), logid)
            raise CozeAPIError(code, msg, logid, debug_url)
        if isinstance(cast, List):
            item_cast = cast[0]
            return [item_cast.model_validate(item) for item in data]
        elif hasattr(cast, "__origin__") and cast.__origin__ is ListResponse:  # type: ignore
            item_cast = get_args(cast)[0]
            return ListResponse(response, [item_cast.model_validate(item) for item in data])
        else:
            if cast is None:
                return None

            res = cast.model_validate(data) if data is not None else cast()  # type: ignore
            if hasattr(res, "_raw_response"):
                res._raw_response = response  # type: ignore
            return res  # type: ignore

    def _parse_requests_code_msg(
        self, method: str, url: str, response: Response, data_field: str = "data"
    ) -> Tuple[Optional[int], str, Optional[str], Any]:
        try:
            response.read()
            body = response.json()
            logid = response.headers.get("x-tt-logid")
            log_debug("request %s#%s responding, logid=%s, data=%s", method, url, logid, body)
        except Exception as e:  # noqa: E722
            raise CozeAPIError(
                response.status_code,
                response.text,
                response.headers.get("x-tt-logid"),
            ) from e
        return self._format_requests_code_msg(method, url, body, data_field)

    async def _aparse_requests_code_msg(
        self, method: str, url: str, response: Response, data_field: str = "data"
    ) -> Tuple[Optional[int], str, Optional[str], Any]:
        try:
            await response.aread()
            body = response.json()
            logid = response.headers.get("x-tt-logid")
            log_debug("request %s#%s responding, logid=%s, data=%s", method, url, logid, body)
        except Exception as e:  # noqa: E722
            raise CozeAPIError(
                response.status_code,
                response.text,
                response.headers.get("x-tt-logid"),
            ) from e
        return self._format_requests_code_msg(method, url, body, data_field)

    def _format_requests_code_msg(
        self,
        method: str,
        url: str,
        body: Dict[str, Any],
        data_field: str = "data",
    ) -> Tuple[Optional[int], str, Optional[str], Any]:
        debug_url = body.get("debug_url")
        if "code" in body and "msg" in body and int(body["code"]) > 0:
            return int(body["code"]), body["msg"], debug_url, body.get(data_field)
        if "error_code" in body and body["error_code"] in COZE_PKCE_AUTH_ERROR_TYPE_ENUMS:
            return None, body["error_code"], debug_url, None
        if "error_message" in body and body["error_message"] != "":
            return None, body["error_message"], debug_url, None
        if data_field in body or "debug_url" in body:
            if "first_id" in body:
                return (
                    0,
                    "",
                    debug_url,
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
                    debug_url,
                    {
                        "data": body.get(data_field),
                        "debug_url": debug_url or "",
                        "execute_id": body.get("execute_id") or None,
                    },
                )
            return 0, "", debug_url, body[data_field]
        if data_field == "data.data":
            return 0, "", debug_url, body["data"]["data"]
        return 0, "", debug_url, body
