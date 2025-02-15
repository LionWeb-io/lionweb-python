from typing import Optional

from lionwebpython.model.structured_data_type_instance import \
    StructuredDataTypeInstance


class StructuredDataTypeInstanceUtils:
    """Utility methods for working with StructuredDataTypeInstances."""

    @staticmethod
    def get_field_value_by_name(instance: StructuredDataTypeInstance, field_name: str):
        """
        Get the field value by the field name.

        Args:
            instance (StructuredDataTypeInstance): The instance from which to retrieve the field value.
            field_name (str): The name of the field.

        Returns:
            Any: The value of the field.

        Raises:
            ValueError: If the field does not exist.
        """
        if instance is None:
            raise ValueError("instance should not be null")
        if field_name is None:
            raise ValueError("field_name should not be null")

        field = instance.get_structured_data_type().get_field_by_name(field_name)
        if field is None:
            raise ValueError(
                f"StructuredDataType {instance.get_structured_data_type().get_name()} does not contain a field named {field_name}"
            )
        return instance.get_field_value(field)

    @staticmethod
    def set_field_value_by_name(
        instance: StructuredDataTypeInstance, field_name: str, value: Optional[object]
    ):
        """
        Set the field value by the field name.

        Args:
            instance (StructuredDataTypeInstance): The instance for which to set the field value.
            field_name (str): The name of the field.
            value (Any): The value to set.

        Raises:
            ValueError: If the field does not exist.
            RuntimeError: If the StructuredDataType is None.
        """
        if instance is None:
            raise ValueError("instance should not be null")
        if field_name is None:
            raise ValueError("field_name should not be null")

        structured_data_type = instance.get_structured_data_type()
        if structured_data_type is None:
            raise RuntimeError(
                f"StructuredDataType should not be null for instance {instance} of class {instance.__class__.__name__}"
            )

        field = instance.get_structured_data_type().get_field_by_name(field_name)
        if field is None:
            raise ValueError(
                f"StructuredDataType {structured_data_type.get_name()} does not contain a field named {field_name}"
            )

        instance.set_field_value(field, value)
