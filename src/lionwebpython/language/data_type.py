from typing import Optional

from lionwebpython.language.language import Language
from lionwebpython.language.language_entity import LanguageEntity
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.model.impl.m3node import M3Node


class DataType(LanguageEntity[M3Node]):
    def __init__(
        self,
        lion_web_version: Optional[LionWebVersion] = None,
        language: Optional[Language] = None,
        name: Optional[str] = None,
        id: Optional[str] = None,
    ):
        if lion_web_version is None:
            lion_web_version = LionWebVersion.current_version()

        super().__init__(lion_web_version=lion_web_version, language=language)
        self.set_id(id)
        self.set_parent(language)
        self.set_name(name)
