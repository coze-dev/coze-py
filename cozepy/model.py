from typing import TypeVar, Generic, List

from pydantic import BaseModel, ConfigDict

T = TypeVar("T", bound=BaseModel)


class CozeModel(BaseModel):
    model_config = ConfigDict(
        protected_namespaces=()
    )


class PagedBase(Generic[T]):
    """
    list api result base.
    """

    def __init__(self, items: List[T], has_more: bool):
        self.items = items
        self.has_more = has_more

    def __repr__(self):
        return f"PagedBase(items={self.items}, has_more={self.has_more})"


class TokenPaged(PagedBase[T]):
    """
    list api, which params is page_token + page_size,
    return is next_page_token + has_more.
    """

    def __init__(self, items: List[T], next_page_token: str = '', has_more: bool = None):
        has_more = has_more if has_more is not None else next_page_token != ''
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
        return f"NumberPaged(items={self.items}, page_num={self.page_num}, page_size={self.page_size}, total={self.total})"
