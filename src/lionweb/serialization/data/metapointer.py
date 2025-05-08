from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional


@dataclass(frozen=True, eq=True)
class MetaPointer:
    if TYPE_CHECKING:
        from lionweb.language import Feature, Language, LanguageEntity
        from lionweb.language.ikeyed import IKeyed

    language: Optional[str] = None
    version: Optional[str] = None
    key: Optional[str] = None

    @staticmethod
    def from_feature(feature: "Feature") -> "MetaPointer":
        return MetaPointer.from_keyed(feature, feature.get_declaring_language())

    @staticmethod
    def from_language_entity(language_entity: "LanguageEntity") -> "MetaPointer":
        key = language_entity.get_key()
        language = language_entity.language
        version = None
        language_key = None

        if language:
            language_key = language.get_key()
            if language.get_version():
                version = language.get_version()

        return MetaPointer(key=key, version=version, language=language_key)

    @staticmethod
    def from_keyed(element_with_key: "IKeyed", language: "Language") -> "MetaPointer":
        key = element_with_key.get_key()
        version = None
        language_key = None

        if language:
            language_key = language.get_key()
            if language.get_version():
                version = language.get_version()

        return MetaPointer(key=key, version=version, language=language_key)

    def __str__(self) -> str:
        return f"MetaPointer(key='{self.key}', version='{self.version}', language='{self.language}')"

    def __repr__(self) -> str:
        return self.__str__()
