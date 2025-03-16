from typing import Optional

from serialization.simple_node import SimpleNode

from lionwebpython.language.concept import Concept
from lionwebpython.language.property import Property


class IntLiteral(SimpleNode):
    def __init__(self, value: int, id: Optional[str] = None):
        super().__init__()
        self.value = value
        if id is not None:
            self.id = id
        else:
            self.assign_random_id()

    def get_classifier(self) -> Concept:
        from serialization.simplemath.simple_math_language import \
            SimpleMathLanguage

        return SimpleMathLanguage.INT_LITERAL

    def __eq__(self, other):
        if not isinstance(other, IntLiteral):
            return False
        return self.get_id() == other.get_id() and self.value == other.value

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return f"IntLiteral{{value={self.value}}}"

    def concrete_get_property_value(self, property: Property):
        if property.get_name() == "value":
            return self.value
        return super().concrete_get_property_value(property)
