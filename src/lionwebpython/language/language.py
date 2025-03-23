from typing import TYPE_CHECKING, List, Optional, TypeVar, cast

from lionwebpython.language.ikeyed import IKeyed
from lionwebpython.language.namespace_provider import NamespaceProvider
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.model.impl.m3node import M3Node

T = TypeVar("T", bound=M3Node)


class Language(M3Node["Language"], NamespaceProvider, IKeyed["Language"]):
    if TYPE_CHECKING:
        from lionwebpython.language.concept import Concept
        from lionwebpython.language.enumeration import Enumeration
        from lionwebpython.language.interface import Interface
        from lionwebpython.language.language_entity import LanguageEntity
        from lionwebpython.language.primitive_type import PrimitiveType
        from lionwebpython.language.structured_data_type import \
            StructuredDataType
        from lionwebpython.model.reference_value import ReferenceValue
        from lionwebpython.self.lioncore import LionCore
        from lionwebpython.utils.language_validator import LanguageValidator
        from lionwebpython.utils.validation_result import ValidationResult

    def __init__(
        self,
        name: Optional[str] = None,
        id: Optional[str] = None,
        key: Optional[str] = None,
        version: Optional[str] = None,
        lion_web_version: Optional[LionWebVersion] = None,
    ):
        super().__init__(lion_web_version or LionWebVersion.current_version())
        if name:
            self.set_name(name)
        if id:
            self.set_id(id)
        if key:
            self.set_key(key)
        if version:
            self.set_version(version)

    def set_name(self, name: Optional[str]) -> "Language":
        self.set_property_value(property_name="name", value=name)
        return self

    def set_version(self, version: Optional[str]) -> "Language":
        self.set_property_value(property_name="version", value=version)
        return self

    def set_key(self, key: str) -> "Language":
        self.set_property_value(property_name="key", value=key)
        return self

    @property
    def key(self):
        return cast(str, self.get_property_value(property_name="key"))

    @key.setter
    def key(self, new_value):
        self.set_property_value(property_name="key", value=new_value)

    @property
    def version(self):
        return cast(str, self.get_property_value(property_name="version"))

    @version.setter
    def version(self, new_value):
        self.set_property_value(property_name="version", value=new_value)

    def namespace_qualifier(self) -> str:
        name = self.get_name()
        if name:
            return name
        else:
            raise ValueError()

    def depends_on(self) -> List["Language"]:
        return self.get_reference_multiple_value("dependsOn")

    def get_elements(self) -> List["LanguageEntity"]:
        return self.get_containment_multiple_value("entities")

    def add_dependency(self, dependency: "Language") -> "Language":
        from lionwebpython.model.reference_value import ReferenceValue

        self.add_reference_multiple_value(
            "dependsOn", ReferenceValue(dependency, dependency.get_name())
        )
        return dependency

    def add_element(self, element: T) -> T:
        self.add_containment_multiple_value("entities", element)
        element.set_parent(self)
        return element

    def get_concept_by_name(self, name: str) -> Optional["Concept"]:
        from lionwebpython.language.concept import Concept

        return next(
            (
                e
                for e in self.get_elements()
                if isinstance(e, Concept) and e.get_name() == name
            ),
            None,
        )

    def get_enumeration_by_name(self, name: str) -> Optional["Enumeration"]:

        from lionwebpython.language.enumeration import Enumeration

        return next(
            (
                e
                for e in self.get_elements()
                if isinstance(e, Enumeration) and e.get_name() == name
            ),
            None,
        )

    def require_concept_by_name(self, name: str) -> "Concept":
        concept = self.get_concept_by_name(name)
        if not concept:
            raise ValueError(f"Concept named {name} was not found")
        return concept

    def get_interface_by_name(self, name: str) -> Optional["Interface"]:
        from lionwebpython.language.interface import Interface

        return next(
            (
                e
                for e in self.get_elements()
                if isinstance(e, Interface) and e.get_name() == name
            ),
            None,
        )

    def get_name(self) -> Optional[str]:
        return cast(Optional[str], self.get_property_value(property_name="name"))

    def get_key(self) -> str:
        return cast(str, self.get_property_value(property_name="key"))

    def get_version(self) -> Optional[str]:
        return cast(Optional[str], self.get_property_value(property_name="version"))

    def get_element_by_name(self, name: str) -> Optional["LanguageEntity"]:
        return next((e for e in self.get_elements() if e.get_name() == name), None)

    def get_primitive_type_by_name(self, name: str) -> Optional["PrimitiveType"]:
        element = self.get_element_by_name(name)
        from lionwebpython.language.primitive_type import PrimitiveType

        if isinstance(element, PrimitiveType):
            return element
        elif element:
            raise RuntimeError(f"Element {name} is not a PrimitiveType")
        return None

    def get_classifier(self) -> "Concept":
        from lionwebpython.self.lioncore import LionCore

        return LionCore.get_language(self.get_lionweb_version())

    def __str__(self) -> str:
        return f"{super().__str__()}{{name={self.get_name()}}}"

    def get_primitive_types(self) -> List["PrimitiveType"]:
        from lionwebpython.language.primitive_type import PrimitiveType

        return [e for e in self.get_elements() if isinstance(e, PrimitiveType)]

    def is_valid(self) -> bool:
        from lionwebpython.utils.language_validator import LanguageValidator

        return LanguageValidator().is_valid(self)

    def validate(self) -> "ValidationResult":
        from lionwebpython.utils.language_validator import LanguageValidator

        return LanguageValidator().validate(self)

    def get_structured_data_types(self) -> List["StructuredDataType"]:
        from lionwebpython.language.structured_data_type import \
            StructuredDataType

        return [e for e in self.get_elements() if isinstance(e, StructuredDataType)]
