from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from lionwebpython.language.INamed import INamed

T = TypeVar('T')

class IKeyed(INamed, ABC, Generic[T]):
    """
    Any element in a Language (M2) that can be referred from an instance (M1).
    """

    @abstractmethod
    def get_key(self) -> str:
        """
        Returns the key of the object.
        """
        pass

    @abstractmethod
    def set_key(self, value: str) -> T:
        """
        Sets the key of the object and returns an instance of the object.
        """
        pass