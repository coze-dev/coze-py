from typing import (
    TYPE_CHECKING,
    TypeVar,
)

from pydantic import BaseModel

if TYPE_CHECKING:
    pass

T = TypeVar("T", bound=BaseModel)
