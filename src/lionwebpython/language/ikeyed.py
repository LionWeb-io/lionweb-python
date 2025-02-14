from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T", bound="IKeyed")


class IKeyed(ABC, Generic[T]):
    @abstractmethod
    def get_key(self) -> str:
        pass

    @abstractmethod
    def set_key(self, value: str) -> T:
        pass
