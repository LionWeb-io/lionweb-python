from lionwebpython.language.enumeration import Enumeration
from lionwebpython.language.enumeration_literal import EnumerationLiteral
from lionwebpython.model.impl.enumeration_value import EnumerationValue


class EnumerationValueImpl(EnumerationValue):
    """This represents an Enumeration Value when the actual Enum class is not available."""

    def __init__(self, enumeration_literal: EnumerationLiteral):
        if enumeration_literal is None:
            raise ValueError("EnumerationLiteral cannot be None")
        self.enumeration_literal = enumeration_literal

    def get_enumeration(self) -> Enumeration:
        el = self.enumeration_literal
        if el is None:
            raise ValueError()
        en = el.get_enumeration()
        if en is None:
            raise ValueError
        return en

    def __eq__(self, other):
        if not isinstance(other, EnumerationValueImpl):
            return False
        return self.enumeration_literal == other.enumeration_literal

    def __hash__(self):
        return hash(self.enumeration_literal)

    def get_enumeration_literal(self) -> EnumerationLiteral:
        return self.enumeration_literal

    def __str__(self):
        return f"EnumerationValue({self.enumeration_literal.get_enumeration().get_name()}.{self.enumeration_literal.get_name()})"
