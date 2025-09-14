import threading
from typing import ClassVar, Optional, Self

from lionweb.serialization.data.metapointer import MetaPointer


class SerializedPropertyValue:
    """
    SerializedPropertyValue with interning to avoid creating duplicate instances.
    """

    # Class-level cache for interning instances
    _instances: ClassVar[
        dict[tuple[MetaPointer, Optional[str]], "SerializedPropertyValue"]
    ] = {}
    _lock = threading.Lock()  # Thread-safe access to cache

    _meta_pointer: MetaPointer
    _value: Optional[str]

    def __new__(cls, meta_pointer: MetaPointer, value: Optional[str] = None):
        # Create cache key
        cache_key = (meta_pointer, value)

        # Thread-safe cache lookup
        with cls._lock:
            if cache_key in cls._instances:
                return cls._instances[cache_key]

            # Create new instance and cache it
            instance = super().__new__(cls)
            instance._meta_pointer = meta_pointer
            instance._value = value
            cls._instances[cache_key] = instance
            return instance

    def __init__(self, meta_pointer: MetaPointer, value: Optional[str] = None):
        # no-op; kept for signature compatibility
        pass

    @classmethod
    def of(cls, meta_pointer: MetaPointer, value: Optional[str] = None) -> Self:
        """
        Factory method to get an interned SerializedPropertyValue instance.
        This is the preferred way to create SerializedPropertyValue instances.
        """
        return cls(meta_pointer, value)

    def get_meta_pointer(self) -> MetaPointer:
        return self._meta_pointer

    @property
    def meta_pointer(self) -> MetaPointer:
        return self._meta_pointer

    def set_meta_pointer(self, meta_pointer: MetaPointer):
        raise RuntimeError(
            "SerializedPropertyValue instances are immutable after creation"
        )

    def get_value(self) -> Optional[str]:
        return self._value

    @property
    def value(self) -> Optional[str]:
        return self._value

    def set_value(self, value: Optional[str]):
        raise RuntimeError(
            "SerializedPropertyValue instances are immutable after creation"
        )

    @classmethod
    def clear_cache(cls):
        """Clear the interning cache. Useful for testing or memory management."""
        with cls._lock:
            cls._instances.clear()

    @classmethod
    def cache_size(cls) -> int:
        """Get the current size of the interning cache."""
        with cls._lock:
            return len(cls._instances)

    def __str__(self):
        return f"SerializedPropertyValue{{meta_pointer={self._meta_pointer}, value='{self._value}'}}"

    def __eq__(self, other):
        if not isinstance(other, SerializedPropertyValue):
            return False
        # With interning, we can use identity comparison for performance
        if self is other:
            return True
        return self._meta_pointer == other._meta_pointer and self._value == other._value

    def __hash__(self):
        return hash((self._meta_pointer, self._value))

    def __repr__(self):
        return self.__str__()
