import abc
import warnings
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Callable,
    Coroutine,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
    overload,
)

import httpx
from pydantic import BaseModel, ConfigDict
from typing_extensions import SupportsIndex

from cozepy.exception import CozeInvalidEventError
from cozepy.log import log_debug

if TYPE_CHECKING:
    from cozepy.request import Requester

T = TypeVar("T")
SyncPage = TypeVar("SyncPage", bound="PagedBase")
AsyncPage = TypeVar("AsyncPage", bound="AsyncPagedBase")


class HTTPResponse(object):
    def __init__(self, raw_response: httpx.Response):
        self._raw_response = raw_response

    @property
    def logid(self) -> str:
        if self._raw_response is None:
            return ""
        return self._raw_response.headers.get("x-tt-logid")


class CozeModel(BaseModel):
    model_config = ConfigDict(
        protected_namespaces=(),
        arbitrary_types_allowed=True,
    )
    _raw_response: Optional[httpx.Response] = None

    @property
    def response(self) -> HTTPResponse:
        return HTTPResponse(self._raw_response)  # type: ignore


class IteratorHTTPResponse(HTTPResponse, Generic[T]):
    def __init__(self, raw_response: httpx.Response, data: Iterator[T]):
        super().__init__(raw_response)
        self.data = data


class AsyncIteratorHTTPResponse(HTTPResponse, Generic[T]):
    def __init__(self, raw_response: httpx.Response, data: AsyncIterator[T]):
        super().__init__(raw_response)
        self.data = data


class FileHTTPResponse(object):
    def __init__(self, raw_response: httpx.Response):
        self._raw_response = raw_response

    @property
    def response(self) -> HTTPResponse:
        return HTTPResponse(self._raw_response)

    def write_to_file(self, file: Union[str]) -> None:
        with open(file, mode="wb") as f:
            for data in self._raw_response.iter_bytes():
                f.write(data)


class ListResponse(Generic[T]):
    def __init__(self, raw_response: httpx.Response, data: List[T]):
        self.data = data
        self._raw_response = raw_response

    @property
    def response(self) -> HTTPResponse:
        return HTTPResponse(self._raw_response)

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> Iterator[T]:
        return iter(self.data)

    @overload
    def __getitem__(self, key: SupportsIndex) -> T: ...

    @overload
    def __getitem__(self, key: slice) -> List[T]: ...

    def __getitem__(self, key: Union[SupportsIndex, slice]) -> Union[T, List[T]]:
        return self.data[key]

    @overload
    def __setitem__(self, key: SupportsIndex, value: T) -> None: ...

    @overload
    def __setitem__(self, key: slice, value: Iterable[T]) -> None: ...

    def __setitem__(self, key: Union[SupportsIndex, slice], value: Union[T, Iterable[T]]) -> None:
        if isinstance(key, slice):
            if not isinstance(value, Iterable):
                raise TypeError("Can only assign an iterable to slice")
            self.data[key] = value  # type: ignore
        else:
            if isinstance(value, Iterable):
                raise TypeError("Can only assign a single value to index")
            self.data[key] = value

    def __delitem__(self, key: Union[SupportsIndex, slice]) -> None:
        del self.data[key]

    def __contains__(self, key: object) -> bool:
        return key in self.data

    def __reversed__(self) -> Iterator[T]:
        return reversed(self.data)


class HTTPRequest(CozeModel, Generic[T]):
    method: str
    url: str
    params: Optional[dict] = None
    headers: Optional[dict] = None
    json_body: Optional[dict] = None
    files: Optional[dict] = None
    is_async: Optional[bool] = None
    stream: bool = False
    data_field: str = "data"
    cast: Optional[Any] = None

    @property
    def as_httpx(self) -> httpx.Request:
        if self.files is not None and self.json_body:
            files = {}
            for k, v in self.files.items():
                files[k] = v
            for k, v in self.json_body.items():
                files[k] = (None, v)
            return httpx.Request(
                method=self.method,
                url=self.url,
                params=self.params,
                headers=self.headers,
                data={},
                files=files,
            )
        return httpx.Request(
            method=self.method,
            url=self.url,
            params=self.params,
            headers=self.headers,
            json=self.json_body,
            files=self.files,
        )


class PagedBase(Generic[T], abc.ABC):
    @abc.abstractmethod
    def iter_pages(self: SyncPage) -> Iterator[SyncPage]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def items(self) -> List[T]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def has_more(self) -> bool:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def response(self) -> HTTPResponse:
        raise NotImplementedError


class AsyncPagedBase(Generic[T], abc.ABC):
    @abc.abstractmethod
    def iter_pages(self: AsyncPage) -> AsyncIterator[AsyncPage]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def items(self) -> List[T]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def has_more(self) -> bool:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def response(self) -> HTTPResponse:
        raise NotImplementedError


class NumberPagedResponse(Generic[T], abc.ABC):
    @abc.abstractmethod
    def get_total(self) -> Optional[int]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_has_more(self) -> Optional[bool]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_items(self) -> List[T]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def response(self) -> HTTPResponse:
        raise NotImplementedError


class NumberPaged(PagedBase[T]):
    def __init__(
        self,
        page_num: int,
        page_size: int,
        requestor: "Requester",
        request_maker: Callable[[int, int], HTTPRequest],
    ):
        self.page_num = page_num
        self.page_size = page_size

        self._total = None
        self._has_more = None
        self._items = None
        self._http_response: Optional[HTTPResponse] = None

        self._requestor = requestor
        self._request_maker = request_maker

        self._fetch_page()

    def __iter__(self) -> Iterator[T]:  # type: ignore
        for page in self.iter_pages():
            for item in page.items:
                yield item

    def iter_pages(self) -> Iterator["NumberPaged[T]"]:
        yield self

        page_num = self.page_num
        current_page = self
        while NumberPaged._is_page_has_more(current_page):
            page_num += 1
            current_page = NumberPaged(
                page_num=page_num,
                page_size=self.page_size,
                requestor=self._requestor,
                request_maker=self._request_maker,
            )
            yield current_page

    @property
    def response(self) -> HTTPResponse:
        return self._http_response  # type: ignore

    @property
    def items(self) -> List[T]:
        return self._items or cast(List[T], [])

    @property
    def has_more(self) -> bool:
        return NumberPaged._is_page_has_more(self)

    @property
    def total(self) -> int:
        return self._total or 0

    def _fetch_page(self):
        if self._total is not None or self._has_more is not None:
            return
        request: HTTPRequest = self._request_maker(self.page_num, self.page_size)
        res: NumberPagedResponse[T] = self._requestor.send(request)
        self._total = res.get_total()
        self._has_more = res.get_has_more()
        self._items = res.get_items()
        self._http_response = res.response

    @staticmethod
    def _is_page_has_more(page: "NumberPaged[T]") -> bool:
        if page._has_more is not None:
            return page._has_more
        if page._total is not None:
            return page._total > page.page_num * page.page_size
        if page._items is not None and page._items and len(page._items) >= page.page_size:
            return True

        return False


class AsyncNumberPaged(AsyncPagedBase[T]):
    def __init__(
        self,
        page_num: int,
        page_size: int,
        requestor: "Requester",
        request_maker: Callable[[int, int], Coroutine[None, None, HTTPRequest]],
    ):
        self.page_num = page_num
        self.page_size = page_size

        self._total = None
        self._has_more = None
        self._items = None
        self._raw_response: Optional[httpx.Response] = None

        self._requestor = requestor
        self._request_maker = request_maker

    async def __aiter__(self) -> AsyncIterator[T]:
        async for page in self.iter_pages():
            for item in page.items:
                yield item

    async def iter_pages(self) -> AsyncIterator["AsyncNumberPaged[T]"]:
        yield self

        page_num = self.page_num
        current_page = self
        while AsyncNumberPaged._is_page_has_more(current_page):
            page_num += 1
            page: AsyncNumberPaged[T] = await AsyncNumberPaged.build(
                page_num=page_num,
                page_size=self.page_size,
                requestor=self._requestor,
                request_maker=self._request_maker,
            )
            current_page = page
            yield page

    @property
    def response(self) -> HTTPResponse:
        return HTTPResponse(self._raw_response)  # type: ignore

    @property
    def items(self) -> List[T]:
        return self._items or cast(List[T], [])

    @property
    def has_more(self) -> bool:
        return AsyncNumberPaged._is_page_has_more(self)

    @property
    def total(self) -> int:
        return self._total or 0

    async def _fetch_page(self):
        """

        :rtype: object
        """
        if self._total is not None:
            return
        request = await self._request_maker(self.page_num, self.page_size)
        res: NumberPagedResponse[T] = await self._requestor.asend(request)
        self._total = res.get_total()
        self._has_more = res.get_has_more()
        self._items = res.get_items()
        self._raw_response = res._raw_response

    @staticmethod
    def _is_page_has_more(page: "AsyncNumberPaged[T]") -> bool:
        if page._has_more is not None:
            return page._has_more
        if page._total is not None:
            return page._total > page.page_num * page.page_size
        if page._total is not None and page._items and len(page._items) >= page.page_size:
            return True
        return False

    @staticmethod
    async def build(
        page_num: int,
        page_size: int,
        requestor: "Requester",
        request_maker: Callable[[int, int], Coroutine[None, None, HTTPRequest]],
    ) -> "AsyncNumberPaged[T]":
        page: AsyncNumberPaged[T] = AsyncNumberPaged(
            page_num=page_num,
            page_size=page_size,
            requestor=requestor,
            request_maker=request_maker,
        )
        await page._fetch_page()
        return page


class TokenPagedResponse(Generic[T], abc.ABC):
    @abc.abstractmethod
    def get_next_page_token(self) -> Optional[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_has_more(self) -> Optional[bool]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_items(self) -> List[T]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def response(self) -> HTTPResponse:
        raise NotImplementedError


class TokenPaged(PagedBase[T]):
    def __init__(
        self,
        page_token: str,
        page_size: int,
        requestor: "Requester",
        request_maker: Callable[[str, int], HTTPRequest],
    ):
        self.page_token = page_token
        self.page_size = page_size

        self._next_page_token = None
        self._has_more = None
        self._items = None
        self._http_response: Optional[HTTPResponse] = None
        self._total = None

        self._requestor = requestor
        self._request_maker = request_maker

        self._fetch_page()

    def __iter__(self) -> Iterator[T]:  # type: ignore
        for page in self.iter_pages():
            for item in page.items:
                yield item

    def iter_pages(self) -> Iterator["TokenPaged[T]"]:
        yield self

        current_page = self
        while TokenPaged._is_page_has_more(current_page):
            current_page = TokenPaged(
                page_token=current_page._next_page_token or "",
                page_size=self.page_size,
                requestor=self._requestor,
                request_maker=self._request_maker,
            )
            yield current_page

    @property
    def response(self) -> HTTPResponse:
        return self._http_response  # type: ignore

    @property
    def items(self) -> List[T]:
        return self._items or cast(List[T], [])

    @property
    def has_more(self) -> bool:
        return TokenPaged._is_page_has_more(self)

    @property
    def total(self) -> int:
        return self._total or 0

    def _fetch_page(self):
        if self._total is not None or self._has_more is not None:
            return
        request: HTTPRequest = self._request_maker(self.page_token, self.page_size)
        res: TokenPagedResponse[T] = self._requestor.send(request)
        self._next_page_token = res.get_next_page_token()
        self._has_more = res.get_has_more()
        self._items = res.get_items()
        self._http_response = res.response

    @staticmethod
    def _is_page_has_more(page: "TokenPaged[T]") -> bool:
        if page._has_more is not None:
            return page._has_more
        if page._next_page_token is not None and page._next_page_token != "":
            return True
        if page._items is not None and page._items and len(page._items) >= page.page_size:
            return True

        return False


class AsyncTokenPaged(AsyncPagedBase[T]):
    def __init__(
        self,
        page_token: str,
        page_size: int,
        requestor: "Requester",
        request_maker: Callable[[str, int], Coroutine[None, None, HTTPRequest]],
    ):
        self.page_token = page_token
        self.page_size = page_size

        self._next_page_token = None
        self._has_more = None
        self._items = None
        self._raw_response: Optional[httpx.Response] = None
        self._total = None

        self._requestor = requestor
        self._request_maker = request_maker

    async def __aiter__(self) -> AsyncIterator[T]:
        async for page in self.iter_pages():
            for item in page.items:
                yield item

    async def iter_pages(self) -> AsyncIterator["AsyncTokenPaged[T]"]:
        yield self

        current_page = self
        while AsyncTokenPaged._is_page_has_more(current_page):
            page: AsyncTokenPaged[T] = await AsyncTokenPaged.build(
                page_token=current_page._next_page_token or "",
                page_size=self.page_size,
                requestor=self._requestor,
                request_maker=self._request_maker,
            )
            current_page = page
            yield page

    @property
    def response(self) -> HTTPResponse:
        return HTTPResponse(self._raw_response)  # type: ignore

    @property
    def items(self) -> List[T]:
        return self._items or cast(List[T], [])

    @property
    def has_more(self) -> bool:
        return AsyncTokenPaged._is_page_has_more(self)

    @property
    def total(self) -> int:
        return self._total or 0

    async def _fetch_page(self):
        """

        :rtype: object
        """
        if self._next_page_token is not None:
            return
        request = await self._request_maker(self.page_token, self.page_size)
        res: TokenPagedResponse[T] = await self._requestor.asend(request)
        self._next_page_token = res.get_next_page_token()
        self._has_more = res.get_has_more()
        self._items = res.get_items()
        self._raw_response = res._raw_response

    @staticmethod
    def _is_page_has_more(page: "AsyncTokenPaged[T]") -> bool:
        if page._has_more is not None:
            return page._has_more
        if page._next_page_token is not None and page._next_page_token != "":
            return True
        if page._items is not None and page._items and len(page._items) >= page.page_size:
            return True
        return False

    @staticmethod
    async def build(
        page_token: str,
        page_size: int,
        requestor: "Requester",
        request_maker: Callable[[str, int], Coroutine[None, None, HTTPRequest]],
    ) -> "AsyncTokenPaged[T]":
        page: AsyncTokenPaged[T] = AsyncTokenPaged(
            page_token=page_token,
            page_size=page_size,
            requestor=requestor,
            request_maker=request_maker,
        )
        await page._fetch_page()
        return page


class LastIDPagedResponse(Generic[T], abc.ABC):
    @abc.abstractmethod
    def get_first_id(self) -> str: ...

    @abc.abstractmethod
    def get_last_id(self) -> str: ...

    @abc.abstractmethod
    def get_has_more(self) -> bool: ...

    @abc.abstractmethod
    def get_items(self) -> List[T]: ...


class LastIDPaged(PagedBase[T]):
    def __init__(
        self,
        before_id: str,
        after_id: str,
        requestor: "Requester",
        request_maker: Callable[[str, str], HTTPRequest],
    ):
        self.before_id = before_id
        self.after_id = after_id
        self.first_id: Optional[str] = None
        self.last_id: Optional[str] = None
        self._has_more: Optional[bool] = None
        self._items: Optional[List[T]] = None
        self._raw_response: Optional[httpx.Response] = None

        self._requestor = requestor
        self._request_maker = request_maker

        self._fetch_page()

    def __iter__(self) -> Iterator[T]:  # type: ignore
        for page in self.iter_pages():
            for item in page.items:
                yield item

    def iter_pages(self) -> Iterator["LastIDPaged[T]"]:
        yield self

        has_more = self._has_more
        last_id = self.last_id
        while self._check_has_more(has_more, last_id):
            page: LastIDPaged[T] = LastIDPaged(
                before_id="",
                after_id=last_id or "",
                requestor=self._requestor,
                request_maker=self._request_maker,
            )
            has_more = page.has_more
            last_id = page.last_id
            yield page

    @property
    def response(self) -> HTTPResponse:
        return HTTPResponse(self._raw_response)  # type: ignore

    @property
    def items(self) -> List[T]:
        return self._items or []

    @property
    def has_more(self) -> bool:
        if self._has_more is not None:
            return self._has_more
        return self.after_id != ""

    def _fetch_page(self):
        if self.last_id is not None or self._has_more is not None:
            return

        request = self._request_maker(self.before_id, self.after_id)
        res: LastIDPagedResponse[T] = self._requestor.send(request)

        self.first_id = res.get_first_id()
        self.last_id = res.get_last_id()
        self._has_more = res.get_has_more()
        self._items = res.get_items()
        self._raw_response = res._raw_response

    def _check_has_more(self, has_more: Optional[bool] = None, last_id: Optional[str] = None) -> bool:
        if has_more is not None:
            return has_more
        if last_id and last_id != "":
            return True
        return False


class AsyncLastIDPaged(AsyncPagedBase[T]):
    def __init__(
        self,
        before_id: str,
        after_id: str,
        requestor: "Requester",
        request_maker: Callable[[str, str], Coroutine[None, None, HTTPRequest]],
    ):
        self.before_id = before_id
        self.after_id = after_id
        self.first_id = None
        self.last_id = None
        self._has_more = None
        self._items: List[T] = []
        self._raw_response: Optional[httpx.Response] = None

        self._requestor = requestor
        self._request_maker = request_maker

    async def __aiter__(self) -> AsyncIterator[T]:
        async for page in self.iter_pages():
            for item in page.items:
                yield item

    async def iter_pages(self) -> AsyncIterator["AsyncLastIDPaged[T]"]:
        yield self

        has_more = self._has_more
        last_id = self.last_id
        while self._check_has_more(has_more, last_id):
            page: AsyncLastIDPaged[T] = await AsyncLastIDPaged.build(
                before_id="",
                after_id=last_id or "",
                requestor=self._requestor,
                request_maker=self._request_maker,
            )
            has_more = page.has_more
            last_id = page.last_id
            yield page

    @property
    def response(self) -> HTTPResponse:
        return HTTPResponse(self._raw_response)  # type: ignore

    @property
    def items(self) -> List[T]:
        return self._items

    @property
    def has_more(self) -> bool:
        if self._has_more is not None:
            return self._has_more
        return self.after_id != ""

    @staticmethod
    async def build(
        before_id: str,
        after_id: str,
        requestor: "Requester",
        request_maker: Callable[[str, str], Coroutine[None, None, HTTPRequest]],
    ) -> "AsyncLastIDPaged[T]":
        page: AsyncLastIDPaged = AsyncLastIDPaged(
            before_id=before_id,
            after_id=after_id,
            requestor=requestor,
            request_maker=request_maker,
        )
        await page._fetch_page()
        return page

    async def _fetch_page(self):
        if self.last_id is not None or self._has_more is not None:
            return

        request = await self._request_maker(self.before_id, self.after_id)
        res: LastIDPagedResponse[T] = await self._requestor.asend(request)

        self.first_id = res.get_first_id()
        self.last_id = res.get_last_id()
        self._has_more = res.get_has_more()
        self._items = res.get_items()
        self._raw_response = res._raw_response

    def _check_has_more(self, has_more: Optional[bool] = None, last_id: Optional[str] = None) -> bool:
        if has_more is not None:
            return has_more
        if last_id and last_id != "":
            return True
        return False


class Stream(Generic[T]):
    def __init__(
        self,
        raw_response: httpx.Response,
        iters: Iterator[str],
        fields: List[str],
        handler: Callable[[Dict[str, str], httpx.Response], Optional[T]],
    ):
        self._iters = iters
        self._fields = fields
        self._handler = handler
        self._raw_response = raw_response

    @property
    def response(self) -> HTTPResponse:
        return HTTPResponse(self._raw_response)

    def __iter__(self):
        while True:
            event_dict = self._extra_event()
            if not event_dict:
                break
            item = self._handler(event_dict, self._raw_response)
            if item:
                yield item

    def __next__(self):
        while True:
            event_dict = self._extra_event()
            if not event_dict:
                raise StopIteration
            item = self._handler(event_dict, self._raw_response)
            if item:
                return item

    def _extra_event(self) -> Optional[Dict[str, str]]:
        data = dict(map(lambda x: (x, ""), self._fields))
        times = 0

        while times < len(data):
            try:
                line = next(self._iters).strip()
            except StopIteration:
                return None
            if line == "":
                continue

            log_debug("receive event, logid=%s, event=%s", self.response.logid, line)

            field, value = self._extra_field_data(line, data)
            data[field] = value
            times += 1
        return data

    def _extra_field_data(self, line: str, data: Dict[str, str]) -> Tuple[str, str]:
        for field in self._fields:
            if line.startswith(field + ":"):
                if data[field] == "":
                    return field, line[len(field) + 1 :].strip()
                else:
                    raise CozeInvalidEventError(field, line, self.response.logid)
        raise CozeInvalidEventError("", line, self.response.logid)


class AsyncStream(Generic[T]):
    def __init__(
        self,
        iters: AsyncIterator[str],
        fields: List[str],
        handler: Callable[[Dict[str, str], httpx.Response], Optional[T]],
        raw_response: httpx.Response,
    ):
        self._iters = iters
        self._fields = fields
        self._handler = handler
        self._iterator = self.__stream__()
        self._raw_response = raw_response

    @property
    def response(self) -> HTTPResponse:
        return HTTPResponse(self._raw_response)

    async def __aiter__(self) -> AsyncIterator[T]:
        async for item in self._iterator:
            yield item

    async def __anext__(self) -> T:
        return await self._iterator.__anext__()

    async def __stream__(self) -> AsyncIterator[T]:
        data = self._make_data()
        times = 0

        async for line in self._iters:
            line = line.strip()
            if line == "":
                continue

            log_debug("async receive event, logid=%s, event=%s", self.response.logid, line)

            field, value = self._extra_field_data(line, data)
            data[field] = value
            times += 1

            if times >= len(self._fields):
                try:
                    event = self._handler(data, self._raw_response)
                    if event:
                        yield event
                except StopAsyncIteration:
                    return
                data = self._make_data()
                times = 0

    def _extra_field_data(self, line: str, data: Dict[str, str]) -> Tuple[str, str]:
        for field in self._fields:
            if line.startswith(field + ":"):
                if data[field] == "":
                    return field, line[len(field) + 1 :].strip()
                else:
                    raise CozeInvalidEventError(field, line, self.response.logid)
        raise CozeInvalidEventError("", line, self.response.logid)

    def _make_data(self):
        return dict(map(lambda x: (x, ""), self._fields))


class DynamicStrEnum(str, Enum):
    """
    动态字符串枚举基类
    """

    @classmethod
    def _missing_(cls, value):
        # 发出警告
        warnings.warn(f"Unknown {cls.__name__} value: {value}", UserWarning)

        # 创建动态成员
        pseudo_member = str.__new__(cls, value)
        pseudo_member._name_ = f"{value.upper()}".replace(".", "_")
        pseudo_member._value_ = value

        # 标记为动态创建
        pseudo_member._is_dynamic = True

        return pseudo_member

    @property
    def is_dynamic(self) -> bool:
        """
        检查此枚举成员是否为动态创建的
        """
        return getattr(self, "_is_dynamic", False)
