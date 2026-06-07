from abc import abstractmethod
from typing import Optional, TypeVar

from lionweb.language.language_entity import LanguageEntity
from lionweb.language.namespace_provider import NamespaceProvider
from lionweb.lionweb_version import LionWebVersion
from lionweb.model.impl.m3node import M3Node
from lionweb.serialization.data.metapointer import MetaPointer

T = TypeVar("T", bound=M3Node)


class Classifier(LanguageEntity[T], NamespaceProvider):
    """Base class for language entities that classify model nodes and declare features
    (concepts, interfaces, annotations)."""

    from lionweb.language.containment import Containment
    from lionweb.language.feature import Feature
    from lionweb.language.language import Language
    from lionweb.language.link import Link
    from lionweb.language.property import Property
    from lionweb.language.reference import Reference

    def __init__(
        self,
        lion_web_version: LionWebVersion | None = None,
        language: Language | None = None,
        name: str | None = None,
        id: str | None = None,
    ):
        if lion_web_version is not None and not isinstance(lion_web_version, LionWebVersion):
            raise ValueError(
                f"Expected lion_web_version to be an instance of LionWebVersion or None but got {lion_web_version}"
            )
        super().__init__(lion_web_version=lion_web_version, language=language, name=name, id=id)

    def get_feature_by_name(self, name: str) -> Feature | None:
        """Look up a feature (own or inherited) by its name.

        Args:
            name: The name of the feature to find.

        Returns:
            Optional[Feature]: The matching feature, or ``None`` if none is found.
        """
        return next((f for f in self.all_features() if f.get_name() == name), None)

    @abstractmethod
    def direct_ancestors(self) -> list["Classifier"]:
        """Return the classifiers this classifier directly extends or implements."""
        pass

    def all_ancestors(self) -> set["Classifier"]:
        """Compute the transitive closure of all ancestor classifiers.

        Returns:
            set[Classifier]: All ancestors reachable through ``direct_ancestors``.
        """
        result = set()
        ancestors = set(self.direct_ancestors())
        while ancestors:
            ancestor = ancestors.pop()
            if ancestor not in result:
                result.add(ancestor)
                ancestors.update(ancestor.direct_ancestors())
        return result

    def all_features(self) -> list[Feature]:
        """Return the own features combined with the inherited ones (own features take precedence).

        Returns:
            list[Feature]: The combined list of features.
        """
        result = list(self.get_features())
        self.combine_features(result, self.inherited_features())
        return result

    @abstractmethod
    def inherited_features(self) -> list[Feature]:
        """Return the features inherited from ancestor classifiers."""
        pass

    def all_properties(self) -> list[Property]:
        from lionweb.language.property import Property

        return [f for f in self.all_features() if isinstance(f, Property)]

    def all_containments(self) -> list[Containment]:
        from lionweb.language.containment import Containment

        return [f for f in self.all_features() if isinstance(f, Containment)]

    def all_references(self) -> list[Reference]:
        from lionweb.language.reference import Reference

        return [f for f in self.all_features() if isinstance(f, Reference)]

    def all_links(self) -> list[Link]:
        from lionweb.language.link import Link

        return [f for f in self.all_features() if isinstance(f, Link)]

    def get_features(self) -> list[Feature]:
        return self.get_containment_multiple_value("features")

    @property
    def features(self) -> list[Feature]:
        return self.get_features()

    def add_feature(self, feature: Feature) -> "Classifier":
        """Add a feature (own declaration) to this classifier and set its parent.

        Args:
            feature: The feature to add.

        Returns:
            Classifier: This classifier, to allow fluent chaining.
        """
        self.add_containment_multiple_value("features", feature)
        feature.set_parent(self)
        return self

    def namespace_qualifier(self) -> str:
        return self.qualified_name()

    def combine_features(self, features_a: list[Feature], features_b: list[Feature]) -> None:
        """Append to ``features_a`` (in place) the features from ``features_b`` whose meta-pointer
        is not already present in ``features_a``.

        Args:
            features_a: The list to extend; entries already present take precedence.
            features_b: The candidate features to merge in.
        """
        existing_metapointers = {MetaPointer.from_feature(f) for f in features_a}
        for f in features_b:
            meta_pointer = MetaPointer.from_feature(f)
            if meta_pointer not in existing_metapointers:
                existing_metapointers.add(meta_pointer)
                features_a.append(f)

    def get_property_by_name(self, property_name: str) -> Optional["Property"]:
        if property_name is None:
            raise ValueError("property_name should not be null")

        from lionweb.language.property import Property

        return next(
            (
                p
                for p in self.all_features()
                if isinstance(p, Property) and p.get_name() == property_name
            ),
            None,
        )

    def require_property_by_name(self, property_name: str) -> "Property":
        property = self.get_property_by_name(property_name)
        if not property:
            raise ValueError(f"Property named {property_name} was not found")
        return property

    def get_reference_by_name(self, reference_name: str) -> Optional["Reference"]:
        if reference_name is None:
            raise ValueError("reference_name should not be null")

        from lionweb.language.reference import Reference

        return next(
            (
                p
                for p in self.all_features()
                if isinstance(p, Reference) and p.get_name() == reference_name
            ),
            None,
        )

    def require_reference_by_name(self, reference_name: str) -> "Reference":
        reference = self.get_reference_by_name(reference_name)
        if not reference:
            raise ValueError(f"Reference named {reference_name} was not found")
        return reference

    def get_containment_by_name(self, containment_name: str) -> Optional["Containment"]:
        if containment_name is None:
            raise ValueError("containment_name should not be null")

        from lionweb.language.containment import Containment

        return next(
            (
                p
                for p in self.all_features()
                if isinstance(p, Containment) and p.get_name() == containment_name
            ),
            None,
        )

    def get_property_by_meta_pointer(self, meta_pointer: MetaPointer) -> Property | None:
        return next(
            (p for p in self.all_properties() if MetaPointer.from_feature(p) == meta_pointer),
            None,
        )

    def get_containment_by_meta_pointer(self, meta_pointer: MetaPointer) -> Containment | None:
        return next(
            (c for c in self.all_containments() if MetaPointer.from_feature(c) == meta_pointer),
            None,
        )

    def get_reference_by_meta_pointer(self, meta_pointer: MetaPointer) -> Reference | None:
        return next(
            (r for r in self.all_references() if MetaPointer.from_feature(r) == meta_pointer),
            None,
        )
