from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from lionwebpython.language.concept import Concept
from lionwebpython.language.data_type import DataType
from lionwebpython.language.language import Language
from lionwebpython.language.namespace_provider import NamespaceProvider


class StructuredDataType(DataType, NamespaceProvider):
    """
    Represents a collection of named instances of Data Types. They are meant to support a small
    composite of values that semantically form a unit. Instances of StructuredDataTypes have no
    identity, are always copied by value, and SHOULD be immutable. Two instances of a
    StructuredDataType that hold the same values for all fields of that StructuredDataType are
    interchangeable. This is different from the instances of Classifiers which have an identity,
    through their id.
    """

    if TYPE_CHECKING:
        from lionwebpython.language.field import Field

    def __init__(
        self,
        language: Optional[Language] = None,
        name: Optional[str] = None,
        id: Optional[str] = None,
        key: Optional[str] = None,
    ):
        super().__init__(language=language, name=name)
        if id:
            self.set_id(id)
        if key:
            self.set_key(key)

    def add_field(self, field: "Field") -> "StructuredDataType":
        if field is None:
            raise ValueError("field should not be null")
        self.add_containment_multiple_value("fields", field)
        field.set_parent(self)
        return self

    def get_fields(self) -> List["Field"]:
        return self.get_containment_multiple_value("fields")

    def namespace_qualifier(self) -> str:
        return self.qualified_name()

    def get_classifier(self) -> "Concept":
        from lionwebpython.self.lioncore import LionCore

        return LionCore.get_structured_data_type(self.get_lionweb_version())

    def get_field_by_name(self, field_name: str) -> Optional["Field"]:
        if field_name is None:
            raise ValueError("fieldName should not be null")
        return next((f for f in self.get_fields() if f.get_name() == field_name), None)
