import abc
from typing import (
    Generic,
    TypeVar,
)

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class CozeModel(BaseModel):
    model_config = ConfigDict(protected_namespaces=())


class Store(abc.ABC, Generic[T]):
    @abc.abstractmethod
    def get(self, key: str) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def set(self, key: str, data: T, ttl: int) -> None:
        raise NotImplementedError


class FileStore(Store[T]):
    pass
