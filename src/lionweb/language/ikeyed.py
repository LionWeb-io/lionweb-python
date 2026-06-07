from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T", bound="IKeyed")


class IKeyed(Generic[T], ABC):
    """Interface for entities identified by a stable, unique key (in addition to an id)."""

    @abstractmethod
    def get_key(self) -> str:
        """Return the key of this entity.

        Returns:
            str: The key.
        """
        pass

    @abstractmethod
    def set_key(self, value: str) -> T:
        """Set the key of this entity.

        Args:
            value: The new key.

        Returns:
            T: This entity, to allow fluent chaining.
        """
        pass
