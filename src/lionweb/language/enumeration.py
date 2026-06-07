from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from lionweb.language.concept import Concept

from lionweb.language.data_type import DataType
from lionweb.language.enumeration_literal import EnumerationLiteral
from lionweb.language.language import Language
from lionweb.language.namespace_provider import NamespaceProvider
from lionweb.lionweb_version import LionWebVersion


class Enumeration(DataType, NamespaceProvider):
    """A data type defined as a fixed set of named literals."""

    def __init__(
        self,
        lion_web_version: Optional["LionWebVersion"] = None,
        language: Language | None = None,
        name: str | None = None,
        id: str | None = None,
        key: str | None = None,
    ):
        super().__init__(lion_web_version=lion_web_version, language=language, name=name, id=id)
        if key:
            self.set_key(key)

    @property
    def literals(self) -> list[EnumerationLiteral]:
        return self.get_containment_multiple_value("literals")

    def add_literal(self, literal: EnumerationLiteral) -> "Enumeration":
        """Add a literal to this enumeration.

        Args:
            literal: The literal to add.

        Returns:
            Enumeration: This enumeration, to allow fluent chaining.

        Raises:
            ValueError: If ``literal`` is ``None``.
        """
        if literal is None:
            raise ValueError("literal should not be null")
        self.add_containment_multiple_value(link_name="literals", value=literal)
        return self

    def namespace_qualifier(self) -> str:
        raise NotImplementedError("Unsupported operation")

    def get_classifier(self) -> "Concept":
        from lionweb.self.lioncore import LionCore

        return LionCore.get_enumeration(self.get_lionweb_version())

    def get_literal_by_name(self, name: str) -> Optional["EnumerationLiteral"]:
        """Look up a literal by its name.

        Args:
            name: The name of the literal to find.

        Returns:
            Optional[EnumerationLiteral]: The matching literal, or ``None`` if none is found.
        """
        return next(
            (literal for literal in self.literals if literal.get_name() == name),
            None,
        )
