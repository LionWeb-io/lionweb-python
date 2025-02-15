from dataclasses import dataclass
from typing import Optional


@dataclass
class MetaPointer:
    language: Optional[str] = None
    version: Optional[str] = None
    key: Optional[str] = None

    def __init__(self, language: Optional[str] = None, version: Optional[str] = None, key: Optional[str] = None):
        self.language = language
        self.version = version
        self.key = key

    @staticmethod
    def from_feature(feature):
        return MetaPointer.from_keyed(feature, feature.get_declaring_language())

    @staticmethod
    def from_language_entity(language_entity):
        meta_pointer = MetaPointer()
        meta_pointer.key = language_entity.get_key()
        if language_entity.get_language():
            meta_pointer.language = language_entity.get_language().get_key()
            if language_entity.get_language().get_version():
                meta_pointer.version = language_entity.get_language().get_version()
        return meta_pointer

    @staticmethod
    def from_keyed(element_with_key, language):
        meta_pointer = MetaPointer()
        meta_pointer.key = element_with_key.get_key()
        if language:
            meta_pointer.language = language.get_key()
            if language.get_version():
                meta_pointer.version = language.get_version()
        return meta_pointer

    def __eq__(self, other):
        if not isinstance(other, MetaPointer):
            return False
        return (
            self.key == other.key
            and self.version == other.version
            and self.language == other.language
        )

    def __hash__(self):
        return hash((self.key, self.version, self.language))

    def __str__(self):
        return f"MetaPointer{{key='{self.key}', version='{self.version}', language='{self.language}'}}"
