from abc import abstractmethod
from typing import List, Optional, Set, TypeVar

from lionwebpython.language.containment import Containment
from lionwebpython.language.feature import Feature
from lionwebpython.language.language import Language
from lionwebpython.language.language_entity import LanguageEntity
from lionwebpython.language.link import Link
from lionwebpython.language.namespace_provider import NamespaceProvider
from lionwebpython.language.property import Property
from lionwebpython.language.reference import Reference
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.model.impl.m3node import M3Node
from lionwebpython.serialization.data.metapointer import MetaPointer

T = TypeVar("T", bound=M3Node)


class Classifier(LanguageEntity[T], NamespaceProvider):
    def __init__(
        self,
        lion_web_version: Optional[LionWebVersion] = None,
        language: Optional[Language] = None,
        name: Optional[str] = None,
        id: Optional[str] = None,
    ):
        super().__init__(lion_web_version, language, name, id)

    def get_feature_by_name(self, name: str) -> Optional[Feature]:
        return next((f for f in self.all_features() if f.get_name() == name), None)

    @abstractmethod
    def direct_ancestors(self) -> List["Classifier"]:
        pass

    def all_ancestors(self) -> Set["Classifier"]:
        result = set()
        ancestors = set(self.direct_ancestors())
        while ancestors:
            ancestor = ancestors.pop()
            if ancestor not in result:
                result.add(ancestor)
                ancestors.update(ancestor.direct_ancestors())
        return result

    def all_features(self) -> List[Feature]:
        result = list(self.get_features())
        self.combine_features(result, self.inherited_features())
        return result

    @abstractmethod
    def inherited_features(self) -> List[Feature]:
        pass

    def all_properties(self) -> List[Property]:
        return [f for f in self.all_features() if isinstance(f, Property)]

    def all_containments(self) -> List[Containment]:
        return [f for f in self.all_features() if isinstance(f, Containment)]

    def all_references(self) -> List[Reference]:
        return [f for f in self.all_features() if isinstance(f, Reference)]

    def all_links(self) -> List[Link]:
        return [f for f in self.all_features() if isinstance(f, Link)]

    def get_features(self) -> List[Feature]:
        return self.get_containment_multiple_value("features")

    def add_feature(self, feature: Feature) -> "Classifier":
        self.add_containment_multiple_value("features", feature)
        feature.set_parent(self)
        return self

    def namespace_qualifier(self) -> str:
        return self.qualified_name()

    def combine_features(
        self, features_a: List[Feature], features_b: List[Feature]
    ) -> None:
        existing_metapointers = {MetaPointer.from_feature(f) for f in features_a}
        for f in features_b:
            meta_pointer = MetaPointer.from_feature(f)
            if meta_pointer not in existing_metapointers:
                existing_metapointers.add(meta_pointer)
                features_a.append(f)
