from dataclasses import dataclass, field

from lionweb.serialization.data.metapointer import MetaPointer
from lionweb.serialization.data.serialized_containment_value import SerializedContainmentValue
from lionweb.serialization.data.serialized_property_value import SerializedPropertyValue
from lionweb.serialization.data.serialized_reference_value import (
    SerializedReferenceValue,
    SerializedReferenceValueEntry,
)


@dataclass
class SerializedClassifierInstance:
    """The serialized form of a classifier instance (a node or annotation instance).

    Holds the instance's ID, classifier, parent ID, and its serialized
    properties, containments, references, and annotations.
    """

    id: str | None
    classifier: MetaPointer
    properties: list[SerializedPropertyValue] = field(default_factory=list)
    containments: list[SerializedContainmentValue] = field(default_factory=list)
    references: list[SerializedReferenceValue] = field(default_factory=list)
    annotations: list[str | None] = field(default_factory=list)
    parent_node_id: str | None = None

    def get_parent_node_id(self) -> str | None:
        return self.parent_node_id

    def set_parent_node_id(self, parent_node_id: str | None) -> None:
        self.parent_node_id = parent_node_id

    def get_containments(self) -> list[SerializedContainmentValue]:
        return list(self.containments)

    def get_children(self) -> list[str | None]:
        children: list[str | None] = []
        for containment in self.containments:
            children.extend(containment.get_children_ids())
        return list(children)

    def add_property_value(self, property_value: SerializedPropertyValue) -> None:
        self.properties.append(property_value)

    def add_containment_value(self, containment_value: SerializedContainmentValue) -> None:
        self.containments.append(containment_value)

    def add_reference_value(self, reference_value: SerializedReferenceValue) -> None:
        self.references.append(reference_value)

    def get_classifier(self) -> MetaPointer:
        return self.classifier

    def set_classifier(self, classifier: MetaPointer) -> None:
        self.classifier = classifier

    def set_property_value(
        self, property_meta_pointer: MetaPointer, serialized_value: str | None
    ) -> None:
        self.properties.append(SerializedPropertyValue(property_meta_pointer, serialized_value))

    def add_children(
        self, containment_meta_pointer: MetaPointer, children_ids: list[str | None]
    ) -> None:
        self.containments.append(SerializedContainmentValue(containment_meta_pointer, children_ids))

    def add_reference_value_entries(
        self,
        reference_meta_pointer: MetaPointer,
        reference_values: list[SerializedReferenceValueEntry],
    ) -> None:
        self.references.append(SerializedReferenceValue(reference_meta_pointer, reference_values))

    def get_property_value_by_key(self, property_key: str) -> str | None:
        for pv in self.properties:
            mp = pv.get_meta_pointer()
            if mp:
                if mp.key == property_key:
                    return pv.get_value()
        return None

    def get_property_value(self, property_meta_pointer) -> str | None:
        for pv in self.properties:
            if property_meta_pointer == pv.get_meta_pointer():
                return pv.get_value()
        return None

    def get_reference_values_by_key(
        self, reference_key: str
    ) -> list[SerializedReferenceValueEntry] | None:
        for rv in self.references:
            meta_pointer = rv.get_meta_pointer()
            if meta_pointer is not None and meta_pointer.key == reference_key:
                return rv.get_value()
        return None

    def get_reference_values(self, reference_meta_pointer) -> list:
        for rv in self.references:
            if reference_meta_pointer == rv.get_meta_pointer():
                return rv.get_value()
        return []

    def get_containment_values_by_key(self, containment_key: str) -> list[str | None]:
        for rv in self.containments:
            if rv.get_meta_pointer().key == containment_key:
                return rv.get_children_ids()
        return []

    def get_containment_values(self, containment_meta_pointer: MetaPointer) -> list[str | None]:
        for cv in self.containments:
            if containment_meta_pointer == cv.get_meta_pointer():
                return cv.get_children_ids()
        return []

    def set_annotations(self, annotation_ids: list[str | None]):
        self.annotations = annotation_ids[:]

    def add_annotation(self, annotation_id: str | None):
        self.annotations.append(annotation_id)

    def __eq__(self, other):
        if not isinstance(other, SerializedClassifierInstance):
            return False
        return (
            self.id == other.id
            and self.classifier == other.classifier
            and self.parent_node_id == other.parent_node_id
            and self.properties == other.properties
            and self.containments == other.containments
            and self.references == other.references
            and self.annotations == other.annotations
        )

    def __hash__(self):
        return hash(
            (
                self.id,
                self.classifier,
                self.parent_node_id,
                tuple(self.properties),
                tuple(self.containments),
                tuple(self.references),
                tuple(self.annotations),
            )
        )

    def __str__(self):
        return (
            f"SerializedClassifierInstance{{id='{self.id}', classifier={self.classifier}, "
            f"parent_node_id='{self.parent_node_id}', properties={self.properties}, "
            f"containments={self.containments}, references={self.references}, "
            f"annotations={self.annotations}}}"
        )
