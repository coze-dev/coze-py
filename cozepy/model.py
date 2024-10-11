import abc
from typing import (
    TYPE_CHECKING,
    AsyncIterator,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

import httpx
from pydantic import BaseModel, ConfigDict

from cozepy.exception import CozeInvalidEventError

if TYPE_CHECKING:
    from cozepy.request import Requester

T = TypeVar("T")
SyncPage = TypeVar("SyncPage", bound="PagedBase")
AsyncPage = TypeVar("AsyncPage", bound="AsyncPagedBase")


class CozeModel(BaseModel):
    model_config = ConfigDict(protected_namespaces=())


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
    cast: Union[Type[T], List[Type[T]], None] = None

    @property
    def as_httpx(self) -> httpx.Request:
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


class NumberPagedResponse(Generic[T], abc.ABC):
    @abc.abstractmethod
    def get_total(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def get_items(self) -> List[T]:
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
        self._items = None

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
        while self.total > page_num * self.page_size:
            page_num += 1
            yield NumberPaged(
                page_num=page_num,
                page_size=self.page_size,
                requestor=self._requestor,
                request_maker=self._request_maker,
            )

    @property
    def items(self) -> List[T]:
        return self._items or cast(List[T], [])

    @property
    def has_more(self) -> bool:
        if self._items and len(self._items) >= self.page_size:
            return True
        return False

    @property
    def total(self) -> int:
        return self._total or 0

    def _fetch_page(self):
        if self._total is not None:
            return
        request: HTTPRequest = self._request_maker(self.page_num, self.page_size)
        res: NumberPagedResponse[T] = self._requestor.send(request)
        self._total = res.get_total()
        self._items = res.get_items()


class AsyncNumberPaged(AsyncPagedBase[T]):
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
        self._items = None

        self._requestor = requestor
        self._request_maker = request_maker

    async def __aiter__(self) -> AsyncIterator[T]:
        async for page in self.iter_pages():
            for item in page.items:
                yield item

    async def iter_pages(self) -> AsyncIterator["AsyncNumberPaged[T]"]:
        yield self

        page_num = self.page_num
        while self.total > page_num * self.page_size:
            page_num += 1
            page: AsyncNumberPaged[T] = await AsyncNumberPaged.build(
                page_num=page_num,
                page_size=self.page_size,
                requestor=self._requestor,
                request_maker=self._request_maker,
            )
            yield page

    @property
    def items(self) -> List[T]:
        return self._items or cast(List[T], [])

    @property
    def has_more(self) -> bool:
        if self._items and len(self._items) >= self.page_size:
            return True
        return False

    @property
    def total(self) -> int:
        return self._total or 0

    async def _fetch_page(self):
        """

        :rtype: object
        """
        if self._total is not None:
            return
        request = self._request_maker(self.page_num, self.page_size)
        res: NumberPagedResponse[T] = await self._requestor.asend(request)
        self._total = res.get_total()
        self._items = res.get_items()

    @staticmethod
    async def build(
        page_num: int,
        page_size: int,
        requestor: "Requester",
        request_maker: Callable[[int, int], HTTPRequest],
    ) -> "AsyncNumberPaged[T]":
        page: AsyncNumberPaged[T] = AsyncNumberPaged(
            page_num=page_num,
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
        request_maker: Callable[[str, str], HTTPRequest],
    ):
        self.before_id = before_id
        self.after_id = after_id
        self.first_id = None
        self.last_id = None
        self._has_more = None
        self._items: List[T] = []

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
        request_maker: Callable[[str, str], HTTPRequest],
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

        request = self._request_maker(self.before_id, self.after_id)
        res: LastIDPagedResponse[T] = await self._requestor.asend(request)

        self.first_id = res.get_first_id()
        self.last_id = res.get_last_id()
        self._has_more = res.get_has_more()
        self._items = res.get_items()

    def _check_has_more(self, has_more: Optional[bool] = None, last_id: Optional[str] = None) -> bool:
        if has_more is not None:
            return has_more
        if last_id and last_id != "":
            return True
        return False


class Stream(Generic[T]):
    def __init__(
        self, iters: Iterator[str], fields: List[str], handler: Callable[[Dict[str, str], str], T], logid: str
    ):
        self._iters = iters
        self._fields = fields
        self._handler = handler
        self._logid = logid

    def __iter__(self):
        return self

    def __next__(self) -> T:
        return self._handler(self._extra_event(), self._logid)

    def _extra_event(self) -> Dict[str, str]:
        data = dict(map(lambda x: (x, ""), self._fields))
        times = 0

        while times < len(data):
            line = next(self._iters).strip()
            if line == "":
                continue

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
                    raise CozeInvalidEventError(field, line, self._logid)
        raise CozeInvalidEventError("", line, self._logid)


class AsyncStream(Generic[T]):
    def __init__(
        self,
        iters: AsyncIterator[str],
        fields: List[str],
        handler: Callable[[Dict[str, str], str], T],
        logid: str,
    ):
        self._iters = iters
        self._fields = fields
        self._handler = handler
        self._logid = logid
        self._iterator = self.__stream__()

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

            field, value = self._extra_field_data(line, data)
            data[field] = value
            times += 1

            if times >= len(self._fields):
                try:
                    yield self._handler(data, self._logid)
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
                    raise CozeInvalidEventError(field, line, self._logid)
        raise CozeInvalidEventError("", line, self._logid)

    def _make_data(self):
        return dict(map(lambda x: (x, ""), self._fields))
