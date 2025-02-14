from typing import List, Optional

from lionwebpython.language.containment import Containment
from lionwebpython.language.property import Property
from lionwebpython.language.reference import Reference
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.model.impl.abstract_classifier_instance import \
    AbstractClassifierInstance
from lionwebpython.model.node import Node
from lionwebpython.model.reference_value import ReferenceValue

# STUB


class M3Node(AbstractClassifierInstance, Node):

    def __init__(self, lion_web_version: LionWebVersion):
        raise ValueError("NOT TRANSLATED YET")

    def set_id(self, id: str) -> "M3Node":
        raise ValueError("NOT TRANSLATED YET")

    def set_parent(self, parent: Node) -> "M3Node":
        raise ValueError("NOT TRANSLATED YET")

    def get_root(self) -> Node:
        raise ValueError("NOT TRANSLATED YET")

    def get_parent(self) -> Node:
        raise ValueError("NOT TRANSLATED YET")

    def get_containment_feature(self) -> Containment:
        raise ValueError("NOT TRANSLATED YET")

    def get_property_value(
        self, property: Property, default_value: object
    ) -> Optional[object]:
        raise ValueError("NOT TRANSLATED YET")

    def set_property_value(self, property: Property, value: object) -> None:
        raise ValueError("NOT TRANSLATED YET")

    def get_children(self, containment: Containment) -> List:
        raise ValueError("NOT TRANSLATED YET")

    def add_child(self, containment: Containment, child: Node) -> None:
        raise ValueError("NOT TRANSLATED YET")

    def remove_child(self, **kwargs) -> None:
        raise ValueError("NOT TRANSLATED YET")

    def get_reference_values(self, reference: Reference) -> List:
        raise ValueError("NOT TRANSLATED YET")

    def add_reference_value(
        self, reference: Reference, reference_value: ReferenceValue
    ) -> None:
        raise ValueError("NOT TRANSLATED YET")

    def set_reference_values(self, reference: Reference, values: List) -> None:
        raise ValueError("NOT TRANSLATED YET")

    def get_id(self) -> Optional[str]:
        raise ValueError("NOT TRANSLATED YET")

    def __str__(self) -> str:
        raise ValueError("NOT TRANSLATED YET")

    def get_containment_single_value(self, link_name: str) -> "M3Node":
        raise ValueError("NOT TRANSLATED YET")

    def get_reference_single_value(self, link_name: str) -> ReferenceValue:
        raise ValueError("NOT TRANSLATED YET")

    def get_containment_multiple_value(self, link_name: str) -> List:
        raise ValueError("NOT TRANSLATED YET")

    def get_reference_multiple_value(self, link_name: str) -> List:
        raise ValueError("NOT TRANSLATED YET")

    def set_containment_single_value(self, link_name: str, value: Node) -> None:
        raise ValueError("NOT TRANSLATED YET")

    def set_reference_single_value(self, link_name: str, value: ReferenceValue) -> None:
        raise ValueError("NOT TRANSLATED YET")

    def add_containment_multiple_value(self, link_name: str, value: Node) -> bool:
        raise ValueError("NOT TRANSLATED YET")

    def add_reference_multiple_value(
        self, link_name: str, value: ReferenceValue
    ) -> None:
        raise ValueError("NOT TRANSLATED YET")

    def get_lion_web_version(self) -> LionWebVersion:
        raise ValueError("NOT TRANSLATED YET")
