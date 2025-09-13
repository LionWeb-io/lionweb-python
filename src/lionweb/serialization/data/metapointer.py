
from typing import Optional, Dict, Tuple
import threading
from lionweb.serialization.data.language_version import LanguageVersion


class MetaPointer:
    """
    MetaPointer with interning to avoid creating duplicate instances.
    Uses LanguageVersion instead of separate language_key and language_version.
    """

    # Class-level cache for interning instances
    _instances: Dict[Tuple[Optional[LanguageVersion], Optional[str]], 'MetaPointer'] = {}
    _lock = threading.Lock()  # Thread-safe access to cache

    def __new__(cls, language_version: Optional[LanguageVersion] = None, key: Optional[str] = None):
        # Create cache key
        cache_key = (language_version, key)

        # Thread-safe cache lookup
        with cls._lock:
            if cache_key in cls._instances:
                return cls._instances[cache_key]

            # Create new instance and cache it
            instance = super().__new__(cls)
            cls._instances[cache_key] = instance
            return instance

    def __init__(self, language_version: Optional[LanguageVersion] = None, key: Optional[str] = None):
        # Only initialize if not already initialized (due to interning)
        if not hasattr(self, '_initialized'):
            self._language_version = language_version
            self._key = key
            self._initialized = True

    @classmethod
    def of(cls, language_version: Optional[LanguageVersion] = None, key: Optional[str] = None) -> 'MetaPointer':
        """
        Factory method to get an interned MetaPointer instance.
        This is the preferred way to create MetaPointer instances.
        """
        return cls(language_version, key)

    @classmethod
    def from_language_entity(cls, entity) -> 'MetaPointer':
        """Create MetaPointer from a language entity."""
        language = entity.language if hasattr(entity, 'language') else None
        language_version = LanguageVersion.of(language.get_key(), language.get_version()) if language else None
        entity_key = entity.get_key() if hasattr(entity, 'get_key') else entity.id
        return cls.of(language_version, entity_key)

    @classmethod
    def from_keyed(cls, keyed, language) -> 'MetaPointer':
        """Create MetaPointer from a keyed object and language."""
        language_version = LanguageVersion.of(language.get_key(), language.get_version()) if language else None
        entity_key = keyed.get_key() if hasattr(keyed, 'get_key') else keyed.id
        return cls.of(language_version, entity_key)

    @classmethod
    def from_feature(cls, feature) -> 'MetaPointer':
        """Create MetaPointer from a feature."""
        container = feature.get_container() if hasattr(feature, 'get_container') else None
        language = container.language if container else None
        language_version = LanguageVersion.of(language.get_key(), language.get_version()) if language else None
        feature_key = feature.get_key() if hasattr(feature, 'get_key') else feature.id
        return cls.of(language_version, feature_key)

    @property
    def language_version(self) -> Optional[LanguageVersion]:
        return self._language_version

    @property
    def language(self) -> Optional[str]:
        if self._language_version is None:
            return None
        return self._language_version.key

    @property
    def version(self) -> Optional[str]:
        if self._language_version is None:
            return None
        return self._language_version.version

    @property
    def key(self) -> Optional[str]:
        return self._key

    # Backward compatibility properties
    @property
    def language_key(self) -> Optional[str]:
        """Backward compatibility: get language key from LanguageVersion."""
        return self._language_version.key if self._language_version else None

    @property
    def language_version_string(self) -> Optional[str]:
        """Backward compatibility: get language version string from LanguageVersion."""
        return self._language_version.version if self._language_version else None

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
        if not isinstance(other, MetaPointer):
            return False
        # With interning, we can use identity comparison for performance
        if self is other:
            return True
        return (
                self.language_version == other.language_version and
                self.key == other.key
        )

    def __hash__(self):
        return hash((self.language_version, self.key))

    def __str__(self):
        return f"MetaPointer{{language_version='{self.language_version}', key='{self.key}'}}"

    def __repr__(self):
        return self.__str__()