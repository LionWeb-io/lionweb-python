from typing import TYPE_CHECKING, Optional, cast

from lionweb.language.ikeyed import IKeyed
from lionweb.language.namespaced_entity import NamespacedEntity
from lionweb.model.impl.m3node import M3Node


class EnumerationLiteral(M3Node, NamespacedEntity, IKeyed):
    if TYPE_CHECKING:
        from lionweb.language.concept import Concept
        from lionweb.language.enumeration import Enumeration
        from lionweb.lionweb_version import LionWebVersion
        from lionweb.self.lioncore import LionCore

    def __init__(
        self,
        lion_web_version: Optional["LionWebVersion"] = None,
        enumeration: Optional["Enumeration"] = None,
        name: Optional[str] = None,
    ):
        from lionweb.lionweb_version import LionWebVersion

        super().__init__(lion_web_version or LionWebVersion.current_version())

        if enumeration is not None:
            from lionweb.language.enumeration import Enumeration

            if not isinstance(enumeration, Enumeration):
                raise ValueError()
            enumeration.add_literal(self)
            self.set_parent(enumeration)

        if name is not None:
            self.name = name

    @property
    def name(self) -> Optional[str]:
        return cast(Optional[str], self.get_property_value(property_name="name"))

    @name.setter
    def name(self, name: Optional[str]) -> None:
        self.set_property_value(property_name="name", value=name)

    def get_name(self) -> Optional[str]:
        return self.name

    def set_name(self, name: Optional[str]) -> "M3Node":
        self.name = name
        return self

    @property
    def enumeration(self) -> Optional["Enumeration"]:
        parent = self.get_parent()
        from lionweb.language.enumeration import Enumeration

        if parent is None:
            return None
        elif isinstance(parent, Enumeration):
            return parent
        else:
            raise ValueError(
                "The parent of this EnumerationLiteral is not an Enumeration"
            )

    @enumeration.setter
    def enumeration(self, enumeration: Optional["Enumeration"]) -> None:
        self.set_parent(enumeration)

    @property
    def container(self) -> Optional["Enumeration"]:
        return self.enumeration

    def get_container(self) -> Optional["Enumeration"]:
        return self.container

    @property
    def key(self) -> str:
        return cast(str, self.get_property_value(property_name="key"))

    @key.setter
    def key(self, value: str) -> None:
        self.set_property_value(property_name="key", value=value)

    def get_key(self) -> str:
        return self.key

    def set_key(self, value: str) -> None:
        self.key = value

    def get_classifier(self) -> "Concept":
        from lionweb.self.lioncore import LionCore

        return LionCore.get_enumeration_literal(self.get_lionweb_version())
