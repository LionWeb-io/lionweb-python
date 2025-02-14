from typing import List

from lionwebpython.language.containment import Containment
from lionwebpython.language.language_entity import LanguageEntity
from lionwebpython.language.namespace_provider import NamespaceProvider
from lionwebpython.language.reference import Reference
from lionwebpython.lionweb_version import LionWebVersion


class Classifier(LanguageEntity, NamespaceProvider):
    def get_lion_web_version(self) -> LionWebVersion:
        raise ValueError("NOT YET TRANSLATED")

    def all_containments(self) -> List[Containment]:
        raise ValueError("NOT YET TRANSLATED")

    def all_references(self) -> List[Reference]:
        raise ValueError("NOT YET TRANSLATED")
