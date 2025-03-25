from typing import TYPE_CHECKING, Optional, cast

from lionwebpython.language.ikeyed import IKeyed
from lionwebpython.language.namespaced_entity import NamespacedEntity
from lionwebpython.model.impl.m3node import M3Node


class EnumerationLiteral(M3Node, NamespacedEntity, IKeyed):
    if TYPE_CHECKING:
        from lionwebpython.language.concept import Concept
        from lionwebpython.language.enumeration import Enumeration
        from lionwebpython.lionweb_version import LionWebVersion
        from lionwebpython.self.lioncore import LionCore

    def __init__(
        self,
        lion_web_version: Optional["LionWebVersion"] = None,
        enumeration: Optional["Enumeration"] = None,
        name: Optional[str] = None,
    ):
        from lionwebpython.lionweb_version import LionWebVersion

        super().__init__(lion_web_version or LionWebVersion.current_version())

        if enumeration is not None:
            from lionwebpython.language.enumeration import Enumeration

            if not isinstance(enumeration, Enumeration):
                raise ValueError()
            enumeration.add_literal(self)
            self.set_parent(enumeration)

        if name is not None:
            self.set_name(name)

    def get_name(self) -> Optional[str]:
        return cast(Optional[str], self.get_property_value(property_name="name"))

    def set_name(self, name: Optional[str]) -> M3Node:
        self.set_property_value(property_name="name", value=name)
        return self

    def get_enumeration(self) -> Optional["Enumeration"]:
        parent = self.get_parent()
        from lionwebpython.language.enumeration import Enumeration

        if parent is None:
            return None
        elif isinstance(parent, Enumeration):
            return parent
        else:
            raise ValueError(
                "The parent of this EnumerationLiteral is not an Enumeration"
            )

    def set_enumeration(self, enumeration: Optional["Enumeration"]) -> None:
        self.set_parent(enumeration)

    def get_container(self) -> Optional["Enumeration"]:
        return self.get_enumeration()

    def get_classifier(self) -> "Concept":
        from lionwebpython.self.lioncore import LionCore

        return LionCore.get_enumeration_literal(self.get_lionweb_version())

    def get_key(self) -> str:
        return cast(str, self.get_property_value(property_name="key"))

    def set_key(self, key: str) -> "EnumerationLiteral":
        self.set_property_value(property_name="key", value=key)
        return self

    @property
    def key(self):
        return cast(str, self.get_property_value(property_name="key"))

    @key.setter
    def key(self, new_value):
        self.set_property_value(property_name="key", value=new_value)
