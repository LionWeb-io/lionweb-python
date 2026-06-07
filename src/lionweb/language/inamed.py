from abc import ABC, abstractmethod


class INamed(ABC):
    """Interface for entities that have a (possibly absent) name."""

    @abstractmethod
    def get_name(self) -> str | None:
        """Return the name of this entity, or ``None`` if it has none."""
        pass
