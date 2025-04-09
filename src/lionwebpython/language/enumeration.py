from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from lionwebpython.language.concept import Concept

from lionwebpython.language.data_type import DataType
from lionwebpython.language.enumeration_literal import EnumerationLiteral
from lionwebpython.language.language import Language
from lionwebpython.language.namespace_provider import NamespaceProvider
from lionwebpython.lionweb_version import LionWebVersion


class Enumeration(DataType, NamespaceProvider):
    def __init__(
        self,
        lion_web_version: Optional["LionWebVersion"] = None,
        language: Optional[Language] = None,
        name: Optional[str] = None,
    ):
        super().__init__(
            lion_web_version=lion_web_version, language=language, name=name
        )

    def get_literals(self) -> List[EnumerationLiteral]:
        return self.get_containment_multiple_value("literals")

    def add_literal(self, literal: EnumerationLiteral) -> "Enumeration":
        if literal is None:
            raise ValueError("literal should not be null")
        self.add_containment_multiple_value(link_name="literals", value=literal)
        return self

    def namespace_qualifier(self) -> str:
        raise NotImplementedError("Unsupported operation")

    def get_classifier(self) -> "Concept":
        from lionwebpython.self.lioncore import LionCore

        return LionCore.get_enumeration(self.get_lionweb_version())
