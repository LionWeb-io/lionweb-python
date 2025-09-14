import threading
from typing import ClassVar, Optional, Self


class LanguageVersion:
    """
    The pair Language Key and Language Version identify a specific version of a language.
    It is used also in the role of 'UsedLanguage', as specified in the specs.
    """

    # Class-level cache for interning instances
    _instances: ClassVar[
        dict[tuple[Optional[str], Optional[str]], "LanguageVersion"]
    ] = {}
    _lock = threading.Lock()  # Thread-safe access to cache

    _key: Optional[str]
    _version: Optional[str]

    def __new__(cls, key: Optional[str] = None, version: Optional[str] = None):
        # Create cache key
        cache_key = (key, version)

        # Thread-safe cache lookup
        with cls._lock:
            if cache_key in cls._instances:
                return cls._instances[cache_key]

            # Create new instance and cache it
            instance = super().__new__(cls)
            instance._key = key
            instance._version = version
            cls._instances[cache_key] = instance
            return instance

    def __init__(self, key: Optional[str] = None, version: Optional[str] = None):
        # no-op; kept for signature compatibility
        pass

    @classmethod
    def of(cls, key: Optional[str] = None, version: Optional[str] = None) -> Self:
        """
        Factory method to get an interned LanguageVersion instance.
        This is the preferred way to create LanguageVersion instances.
        """
        return cls(key, version)

    @staticmethod
    def from_language(language):
        """
        Create a UsedLanguage instance from a Language object.

        Args:
            language: An object with `key` and `version` attributes.

        Returns:
            LanguageVersion: An instance of UsedLanguage.

        Raises:
            ValueError: If language or its attributes are None.
        """
        if language is None:
            raise ValueError("Language parameter should not be null")
        if language.version is None:
            raise ValueError("Language version should not be null")
        return LanguageVersion(language.key, language.version)

    @staticmethod
    def from_meta_pointer(meta_pointer):
        """
        Create a UsedLanguage instance from a MetaPointer object.

        Args:
            meta_pointer: An object with `language` and `version` attributes.

        Returns:
            LanguageVersion: An instance of UsedLanguage.

        Raises:
            ValueError: If meta_pointer or its attributes are None.
        """
        if meta_pointer is None:
            raise ValueError("meta_pointer parameter should not be null")
        if meta_pointer.language is None:
            raise ValueError("meta_pointer language should not be null")
        if meta_pointer.version is None:
            raise ValueError("meta_pointer version should not be null")
        return LanguageVersion.of(meta_pointer.language, meta_pointer.version)

    def get_key(self) -> Optional[str]:
        return self._key

    def set_key(self, key: str):
        raise RuntimeError("LanguageVersion instances are immutable after creation")

    def get_version(self) -> Optional[str]:
        return self._version

    def set_version(self, version: str):
        raise RuntimeError("LanguageVersion instances are immutable after creation")

    @property
    def key(self) -> Optional[str]:
        return self._key

    @property
    def version(self) -> Optional[str]:
        return self._version

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

    def __eq__(self, other):
        if not isinstance(other, LanguageVersion):
            return False
        # With interning, we can use identity comparison for performance
        if self is other:
            return True
        return self.key == other.key and self.version == other.version

    def __hash__(self):
        return hash((self.key, self.version))

    def __str__(self):
        return f"UsedLanguage{{key='{self.key}', version='{self.version}'}}"
