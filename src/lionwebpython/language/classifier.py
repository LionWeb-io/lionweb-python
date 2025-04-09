from abc import abstractmethod
from typing import List, Optional, Set, TypeVar

from lionwebpython.language.language_entity import LanguageEntity
from lionwebpython.language.namespace_provider import NamespaceProvider
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.model.impl.m3node import M3Node
from lionwebpython.serialization.data.metapointer import MetaPointer

T = TypeVar("T", bound=M3Node)


class Classifier(LanguageEntity[T], NamespaceProvider):
    from lionwebpython.language.containment import Containment
    from lionwebpython.language.feature import Feature
    from lionwebpython.language.language import Language
    from lionwebpython.language.link import Link
    from lionwebpython.language.property import Property
    from lionwebpython.language.reference import Reference

    def __init__(
        self,
        lion_web_version: Optional[LionWebVersion] = None,
        language: Optional[Language] = None,
        name: Optional[str] = None,
        id: Optional[str] = None,
    ):
        if lion_web_version is not None and not isinstance(
            lion_web_version, LionWebVersion
        ):
            raise ValueError(
                f"Expected lion_web_version to be an instance of LionWebVersion or None but got {lion_web_version}"
            )
        super().__init__(
            lion_web_version=lion_web_version, language=language, name=name, id=id
        )

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
        from lionwebpython.language.property import Property

        return [f for f in self.all_features() if isinstance(f, Property)]

    def all_containments(self) -> List[Containment]:
        from lionwebpython.language.containment import Containment

        return [f for f in self.all_features() if isinstance(f, Containment)]

    def all_references(self) -> List[Reference]:
        from lionwebpython.language.reference import Reference

        return [f for f in self.all_features() if isinstance(f, Reference)]

    def all_links(self) -> List[Link]:
        from lionwebpython.language.link import Link

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

    def get_property_by_name(self, property_name: str) -> Optional["Property"]:
        if property_name is None:
            raise ValueError("property_name should not be null")

        from lionwebpython.language.property import Property

        return next(
            (
                p
                for p in self.all_features()
                if isinstance(p, Property) and p.get_name() == property_name
            ),
            None,
        )

    def get_reference_by_name(self, reference_name: str) -> Optional["Reference"]:
        if reference_name is None:
            raise ValueError("reference_name should not be null")

        from lionwebpython.language.reference import Reference

        return next(
            (
                p
                for p in self.all_features()
                if isinstance(p, Reference) and p.get_name() == reference_name
            ),
            None,
        )

    def get_containment_by_name(self, containment_name: str) -> Optional["Containment"]:
        if containment_name is None:
            raise ValueError("containment_name should not be null")

        from lionwebpython.language.containment import Containment

        return next(
            (
                p
                for p in self.all_features()
                if isinstance(p, Containment) and p.get_name() == containment_name
            ),
            None,
        )

    def get_property_by_meta_pointer(
        self, meta_pointer: MetaPointer
    ) -> Optional[Property]:
        return next(
            (
                p
                for p in self.all_properties()
                if MetaPointer.from_feature(p) == meta_pointer
            ),
            None,
        )

    def get_containment_by_meta_pointer(
        self, meta_pointer: MetaPointer
    ) -> Optional[Containment]:
        return next(
            (
                c
                for c in self.all_containments()
                if MetaPointer.from_feature(c) == meta_pointer
            ),
            None,
        )

    def get_reference_by_meta_pointer(
        self, meta_pointer: MetaPointer
    ) -> Optional[Reference]:
        return next(
            (
                r
                for r in self.all_references()
                if MetaPointer.from_feature(r) == meta_pointer
            ),
            None,
        )
