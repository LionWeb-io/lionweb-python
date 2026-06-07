from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from lionweb.language.concept import Concept

from lionweb.language.data_type import DataType
from lionweb.language.ikeyed import IKeyed
from lionweb.language.namespace_provider import NamespaceProvider
from lionweb.language.namespaced_entity import NamespacedEntity
from lionweb.language.structured_data_type import StructuredDataType
from lionweb.model.impl.m3node import M3Node
from lionweb.model.reference_value import ReferenceValue


class Field(M3Node, NamespacedEntity, IKeyed):
    """
    Field of a StructuredDataType.
    """

    def __init__(
        self,
        name: str | None = None,
        type: DataType | None = None,
        id: str | None = None,
        key: str | None = None,
        structured_data_type: StructuredDataType | None = None,
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

    def get_name(self) -> str | None:
        return cast(str | None, self.get_property_value(property="name"))

    def set_name(self, name: str | None) -> None:
        self.set_property_value(property="name", value=name)

    def get_container(self) -> NamespaceProvider | None:
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
        from lionweb.self.lioncore import LionCore

        return LionCore.get_field(self.get_lionweb_version())

    def get_type(self) -> DataType | None:
        return cast(DataType | None, self.get_reference_single_value("type"))

    def set_type(self, type: DataType | None) -> None:
        if type is None:
            self.set_reference_single_value("type", None)
        else:
            self.set_reference_single_value("type", ReferenceValue(type, type.get_name()))

    def get_key(self) -> str:
        return cast(str, self.get_property_value(property="key"))

    def set_key(self, key: str | None) -> "Field":
        self.set_property_value(property="key", value=key)
        return self
