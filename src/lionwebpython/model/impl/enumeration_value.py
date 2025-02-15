from abc import ABC, abstractmethod

from lionwebpython.language.enumeration_literal import EnumerationLiteral


class EnumerationValue(ABC):
    """An enumeration value represented through this interface can be automatically supported by
    the serialization mechanism. Enumeration values can be represented otherwise, but in that case
    the specific serializers and deserializers should be registered.
    """

    @abstractmethod
    def get_enumeration_literal(self) -> EnumerationLiteral:
        """Returns the associated EnumerationLiteral."""
        pass
