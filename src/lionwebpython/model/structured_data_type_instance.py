from abc import ABC, abstractmethod
from typing import Any, Optional

from lionwebpython.language.field import Field
from lionwebpython.language.structured_data_type import StructuredDataType


class StructuredDataTypeInstance(ABC):
    """This represents an instance of Structured Data Type."""

    @abstractmethod
    def get_structured_data_type(self) -> StructuredDataType:
        """The StructuredDataType of which this StructuredDataTypeInstance is an instance."""
        pass

    @abstractmethod
    def get_field_value(self, field: Field) -> Optional[Any]:
        """Get the field value associated with the specified field."""
        pass

    @abstractmethod
    def set_field_value(self, field: Field, value: Optional[Any]) -> None:
        """Set the field value for the specified field.

        Raises:
            ValueError: If the value is not compatible with the field type.
        """
        pass
