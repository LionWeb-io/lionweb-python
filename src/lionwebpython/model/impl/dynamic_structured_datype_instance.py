from typing import Any, Dict, Union

from lionwebpython.language.field import Field
from lionwebpython.language.structured_data_type import StructuredDataType


class DynamicStructuredDataTypeInstance:
    def __init__(self, structured_data_type: StructuredDataType):
        if structured_data_type is None:
            raise ValueError("structuredDataType should not be null")
        self.structured_data_type = structured_data_type
        self.field_values: Dict[Field, Any] = {}

    def get_structured_data_type(self) -> StructuredDataType:
        return self.structured_data_type

    def get_field_value(self, field: Field) -> Any:
        if field is None:
            raise ValueError("field should not be null")
        if field.id is None:
            raise ValueError("Field with no ID specified should not be used")
        if field not in self.structured_data_type.get_fields():
            raise ValueError(
                f"Invalid field for StructuredDataType {self.structured_data_type}"
            )
        return self.field_values.get(field)

    def set_field_value(self, field: Union[Field, str], value: Any):
        if field is None:
            raise ValueError("Field should not be null")
        my_field: Field
        if isinstance(field, str):
            tmp = self.structured_data_type.get_field_by_name(field)
            if tmp is None:
                raise ValueError(f"Cannot find field with name {field}")
            my_field = tmp
        else:
            if field not in self.structured_data_type.get_fields():
                raise ValueError(
                    f"Invalid field for StructuredDataType {self.structured_data_type}"
                )
            my_field = field
        if my_field.id is None:
            raise ValueError("Field with no ID specified should not be used")
        self.field_values[my_field] = value

    def __eq__(self, other):
        if not isinstance(other, DynamicStructuredDataTypeInstance):
            return False
        if self.structured_data_type != other.structured_data_type:
            return False
        for field in self.structured_data_type.get_fields():
            if self.get_field_value(field) != other.get_field_value(field):
                return False
        return True

    def __hash__(self):
        hash_code = hash(self.structured_data_type.structured_id)
        for field in self.structured_data_type.get_fields():
            hash_code += 3 * hash(self.get_field_value(field))
        return hash_code

    def __repr__(self):
        return f"DynamicStructuredDataTypeInstance(structuredDataType={self.structured_data_type}, fieldValues={self.field_values})"
