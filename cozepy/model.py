from typing import Callable, Dict, Generic, Iterator, List, Tuple, TypeVar

from pydantic import BaseModel, ConfigDict

from cozepy.exception import CozeEventError

T = TypeVar("T")


class CozeModel(BaseModel):
    model_config = ConfigDict(protected_namespaces=())


class PagedBase(Generic[T]):
    """
    list api result base.
    """

    def __init__(self, items: List[T], has_more: bool):
        self.items = items
        self.has_more = has_more


class TokenPaged(PagedBase[T]):
    """
    list api, which params is page_token + page_size,
    return is next_page_token + has_more.
    """

    def __init__(self, items: List[T], next_page_token: str = "", has_more: bool = None):
        has_more = has_more if has_more is not None else next_page_token != ""
        super().__init__(items, has_more)
        self.next_page_token = next_page_token

    def __repr__(self):
        return f"TokenPaged(items={self.items}, next_page_token={self.next_page_token})"


class NumberPaged(PagedBase[T]):
    def __init__(self, items: List[T], page_num: int, page_size: int, total: int = None):
        has_more = len(items) >= page_size
        super().__init__(items, has_more)
        self.page_num = page_num
        self.page_size = page_size
        self.total = total

    def __repr__(self):
        return (
            f"NumberPaged(items={self.items}, page_num={self.page_num}, page_size={self.page_size}, total={self.total})"
        )


class LastIDPaged(PagedBase[T]):
    def __init__(
        self,
        items: List[T],
        first_id: str = "",
        last_id: str = "",
        has_more: bool = None,
    ):
        has_more = has_more if has_more is not None else last_id != ""
        super().__init__(items, has_more)
        self.first_id = first_id
        self.last_id = last_id
        self.has_more = has_more

    def __repr__(self):
        return f"LastIDPaged(items={self.items}, first_id={self.first_id}, last_id={self.last_id}, has_more={self.has_more})"


class Stream(Generic[T]):
    def __init__(self, iters: Iterator[str], fields: List[str], handler: Callable[[Dict[str, str]], T], logid: str):
        self._iters = iters
        self._fields = fields
        self._handler = handler
        self._logid = logid

    def __iter__(self):
        return self

    def __next__(self) -> T:
        return self._handler(self._extra_event())

    def _extra_event(self) -> Dict[str, str]:
        data = dict(map(lambda x: (x, ""), self._fields))
        times = 0

        while times < len(data):
            line = next(self._iters)
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
                    raise CozeEventError(field, line, self._logid)
        raise CozeEventError("", line, self._logid)
