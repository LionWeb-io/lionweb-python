from lionweb.language.language import Language
from lionweb.language.language_entity import LanguageEntity
from lionweb.lionweb_version import LionWebVersion
from lionweb.model.impl.m3node import M3Node


class DataType(LanguageEntity[M3Node]):
    """Base class for the data types of a language: primitive types, enumerations, and structured data types."""

    def __init__(
        self,
        lion_web_version: LionWebVersion | None = None,
        language: Language | None = None,
        name: str | None = None,
        id: str | None = None,
    ):
        if lion_web_version is None:
            lion_web_version = LionWebVersion.current_version()

        super().__init__(lion_web_version=lion_web_version, language=language)
        self.set_id(id)
        self.set_parent(language)
        self.set_name(name)
