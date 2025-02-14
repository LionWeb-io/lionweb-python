from typing import List, Set, TypeVar

from lionwebpython.language.containment import Containment
from lionwebpython.language.feature import Feature
from lionwebpython.language.language_entity import LanguageEntity
from lionwebpython.language.namespace_provider import NamespaceProvider
from lionwebpython.language.reference import Reference
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.model.impl.m3node import M3Node

T = TypeVar("T", bound=M3Node)


class Classifier(LanguageEntity[T], NamespaceProvider):
    def get_lion_web_version(self) -> LionWebVersion:
        raise ValueError("NOT YET TRANSLATED")

    def all_containments(self) -> List[Containment]:
        raise ValueError("NOT YET TRANSLATED")

    def all_references(self) -> List[Reference]:
        raise ValueError("NOT YET TRANSLATED")

    def all_ancestors(self) -> Set["Classifier"]:
        raise ValueError("NOT YET TRANSLATED")

    def combine_features(
        self, features_a: List[Feature], features_b: List[Feature]
    ) -> None:
        raise ValueError("NOT YET TRANSLATED")

    def get_features(self) -> List[Feature]:
        raise ValueError("NOT YET TRANSLATED")
