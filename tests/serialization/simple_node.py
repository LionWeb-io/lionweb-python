import random
from typing import List, Optional

from lionweb.language import Containment
from lionweb.language.reference import Reference
from lionweb.model.annotation_instance import AnnotationInstance
from lionweb.model.impl.abstract_classifier_instance import \
    AbstractClassifierInstance
from lionweb.model.node import Node
from lionweb.model.reference_value import ReferenceValue


class SimpleNode(AbstractClassifierInstance, Node):
    def __init__(self):
        self._id: Optional[str] = None
        self.parent: Optional["SimpleNode"] = None
        self.annotations: List["AnnotationInstance"] = []

    def assign_random_id(self):
        random_id = f"id_{abs(random.getrandbits(64))}"
        self.set_id(random_id)

    def set_id(self, node_id: str):
        self._id = node_id

    def set_parent(self, parent: "SimpleNode"):
        self.parent = parent

    def get_id(self) -> Optional[str]:
        return self._id

    def get_parent(self) -> Optional["SimpleNode"]:
        return self.parent

    def get_annotations(self) -> List["AnnotationInstance"]:
        return self.annotations

    def get_containment_feature(self):
        raise NotImplementedError()

    def get_property_value(self, property):
        if property not in self.get_classifier().all_properties():
            raise ValueError("Property not belonging to this concept")
        return self.concrete_get_property_value(property)

    def concrete_get_property_value(self, property):
        raise NotImplementedError(f"Property {property} not yet supported")

    def set_property_value(self, property, value):
        raise NotImplementedError()

    def get_children(self, containment: Optional[Containment] = None):
        if containment is None:
            from lionweb.model.classifier_instance_utils import get_children

            return get_children(self)
        if containment not in self.get_classifier().all_containments():
            raise ValueError("Containment not belonging to this concept")
        return self.concrete_get_children(containment)

    def concrete_get_children(self, containment):
        raise NotImplementedError(f"Containment {containment} not yet supported")

    def add_child(self, containment, child):
        raise NotImplementedError()

    def remove_child(self, node):
        raise NotImplementedError()

    def get_reference_values(self, reference: Reference) -> List["ReferenceValue"]:
        if reference not in self.get_classifier().all_references():
            raise ValueError("Reference not belonging to this concept")
        return self.concrete_get_reference_values(reference)

    def concrete_get_reference_values(
        self, reference: Reference
    ) -> List["ReferenceValue"]:
        raise NotImplementedError(f"Reference {reference} not yet supported")

    def add_reference_value(self, reference, referred_node: Optional["ReferenceValue"]):
        if reference not in self.get_classifier().all_references():
            raise ValueError("Reference not belonging to this concept")
        self.concrete_add_reference_value(reference, referred_node)

    def concrete_add_reference_value(
        self, reference, referred_node: Optional["ReferenceValue"]
    ):
        raise NotImplementedError(f"Reference {reference} not yet supported")

    def get_root(self):
        raise NotImplementedError()

    def remove_child_by_index(self, containment, index: int):
        raise NotImplementedError()

    def remove_reference_value(
        self, reference, reference_value: Optional["ReferenceValue"] = None
    ):
        raise NotImplementedError()

    def remove_reference_value_by_index(self, reference, index: int):
        raise NotImplementedError()

    def set_reference_values(self, reference, values: List["ReferenceValue"]):
        raise NotImplementedError()
