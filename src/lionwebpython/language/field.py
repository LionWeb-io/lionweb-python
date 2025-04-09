from typing import TYPE_CHECKING, Optional, cast

if TYPE_CHECKING:
    from lionwebpython.language.concept import Concept

from lionwebpython.language.data_type import DataType
from lionwebpython.language.ikeyed import IKeyed
from lionwebpython.language.namespace_provider import NamespaceProvider
from lionwebpython.language.namespaced_entity import NamespacedEntity
from lionwebpython.language.structured_data_type import StructuredDataType
from lionwebpython.model.impl.m3node import M3Node
from lionwebpython.model.reference_value import ReferenceValue


class Field(M3Node, NamespacedEntity, IKeyed):
    """
    Field of a StructuredDataType.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        type: Optional[DataType] = None,
        id: Optional[str] = None,
        key: Optional[str] = None,
        structured_data_type: Optional[StructuredDataType] = None,
    ):
        super().__init__()
        if structured_data_type:
            structured_data_type.add_field(self)
            self.set_parent(structured_data_type)
        if name:
            self.set_name(name)
        if type:
            self.set_type(type)
        if id:
            self.set_id(id)
        if key:
            self.set_key(key)

    def get_name(self) -> Optional[str]:
        return cast(Optional[str], self.get_property_value(property_name="name"))

    def set_name(self, name: Optional[str]):
        self.set_property_value(property_name="name", value=name)

    def get_container(self) -> Optional[NamespaceProvider]:
        """
        The container is always the parent. It is just casted for convenience.
        """
        parent = self.get_parent()
        if parent is None:
            return None
        if isinstance(parent, NamespaceProvider):
            return parent
        else:
            raise ValueError("The parent is not a NamespaceProvider")

    def get_classifier(self) -> "Concept":
        from lionwebpython.self.lioncore import LionCore

        return LionCore.get_field(self.get_lionweb_version())

    def get_type(self) -> Optional[DataType]:
        return cast(Optional[DataType], self.get_reference_single_value("type"))

    def set_type(self, type: Optional[DataType]):
        if type is None:
            self.set_reference_single_value("type", None)
        else:
            self.set_reference_single_value(
                "type", ReferenceValue(type, type.get_name())
            )

    def get_key(self) -> str:
        return cast(str, self.get_property_value(property_name="key"))

    def set_key(self, key: Optional[str]) -> "Field":
        self.set_property_value(property_name="key", value=key)
        return self
