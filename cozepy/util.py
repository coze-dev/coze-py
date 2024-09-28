import base64
from typing import (
    TYPE_CHECKING,
    TypeVar,
)

from pydantic import BaseModel

if TYPE_CHECKING:
    pass

T = TypeVar("T", bound=BaseModel)


def base64_encode_string(s: str) -> str:
    return base64.standard_b64encode(s.encode("utf-8")).decode("utf-8")
