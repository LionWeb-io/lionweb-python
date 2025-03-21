import json
from enum import Enum
from typing import Dict, Type, cast

from lionwebpython.language.enumeration import Enumeration
from lionwebpython.language.lioncore_builtins import LionCoreBuiltins
from lionwebpython.language.structured_data_type import StructuredDataType
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.model.impl.dynamic_structured_datype_instance import \
    DynamicStructuredDataTypeInstance
from lionwebpython.model.impl.enumeration_value import EnumerationValue
from lionwebpython.model.impl.enumeration_value_impl import \
    EnumerationValueImpl
from lionwebpython.model.structured_data_type_instance import \
    StructuredDataTypeInstance


class PrimitiveValuesSerialization:
    def __init__(self):
        self.enumerations_by_id = {}
        self.structures_data_types_by_id = {}
        self.dynamic_nodes_enabled = False
        self.primitive_deserializers: Dict[str, object] = {}
        self.primitive_serializers: Dict[str, object] = {}

    def register_language(self, language):
        for element in language.get_elements():
            if isinstance(element, Enumeration):
                self.enumerations_by_id[element.id] = element
            elif isinstance(element, StructuredDataType):
                self.structures_data_types_by_id[element.id] = element

    def enable_dynamic_nodes(self):
        self.dynamic_nodes_enabled = True

    def register_deserializer(self, data_type_id, deserializer):
        self.primitive_deserializers[data_type_id] = deserializer

    def register_serializer(self, data_type_id, serializer):
        self.primitive_serializers[data_type_id] = serializer

    def deserialize_sdt(self, data_type_id, json_obj):
        sdt = self.structures_data_types_by_id[data_type_id]
        sdt_instance = DynamicStructuredDataTypeInstance(sdt)
        for field in sdt.get_fields():
            if field.get_key() in json_obj:
                field_data_type = field.get_type()
                field_value = json_obj[field.get_key()]
                if field_value is None:
                    sdt_instance.set_field_value(field, None)
                elif self.is_structured_data_type(field_data_type.id):
                    sdt_instance.set_field_value(
                        field,
                        self.deserialize_sdt(field_data_type.id, field_value),
                    )
                else:
                    sdt_instance.set_field_value(
                        field, self.deserialize(field_data_type, field_value, False)
                    )
        return sdt_instance

    def deserialize(self, data_type, serialized_value, is_required=False):
        data_type_id = data_type.id
        if data_type_id in self.primitive_deserializers:
            return self.primitive_deserializers[data_type_id](
                serialized_value, is_required
            )
        elif data_type_id in self.enumerations_by_id and self.dynamic_nodes_enabled:
            if serialized_value is None:
                return None
            enumeration = self.enumerations_by_id[data_type_id]
            for literal in enumeration.get_literals():
                if literal.get_key() == serialized_value:
                    return EnumerationValueImpl(literal)
            raise ValueError(f"Invalid enumeration literal value: {serialized_value}")
        elif (
            data_type_id in self.structures_data_types_by_id
            and self.dynamic_nodes_enabled
        ):
            if serialized_value is None:
                return None
            json_obj = json.loads(serialized_value)
            return self.deserialize_sdt(data_type_id, json_obj)
        else:
            raise ValueError(
                f"Unable to deserialize primitive values of type {data_type}"
            )

    def serialize_sdt(self, structured_data_type_instance):
        json_obj = {}
        for (
            field
        ) in structured_data_type_instance.get_structured_data_type().get_fields():
            field_value = structured_data_type_instance.get_field_value(field)
            if field_value is None:
                json_obj[field.get_key()] = None
            elif self.is_structured_data_type(field.get_type().id):
                json_obj[field.get_key()] = self.serialize_sdt(field_value)
            else:
                json_obj[field.get_key()] = self.serialize(
                    field.get_type().id, field_value
                )
        return json_obj

    def serialize(self, primitive_type_id, value):
        if primitive_type_id in self.primitive_serializers:
            return self.primitive_serializers[primitive_type_id](value)
        elif self.is_enum(primitive_type_id):
            if value is None:
                return None
            if isinstance(value, EnumerationValue):
                enumeration_literal = value.get_enumeration_literal()
                return enumeration_literal.get_key()
            elif isinstance(value, Enum):
                enumeration = self.enumerations_by_id.get(primitive_type_id)
                if enumeration is None:
                    raise ValueError(
                        f"Cannot find enumeration with id {primitive_type_id}"
                    )
                return self.serializer_for(type(value), enumeration)(value)
            else:
                raise TypeError(f"Unexpected type for enum: {type(value)}")
        elif self.is_structured_data_type(primitive_type_id):
            if value is None:
                return None
            if isinstance(value, StructuredDataTypeInstance):
                return json.dumps(self.serialize_sdt(value))
            else:
                raise TypeError(
                    f"Expected StructuredDataTypeInstance, got {type(value)}"
                )
        else:
            raise ValueError(
                f"Unable to serialize primitive values of type {primitive_type_id}"
            )

    def is_enum(self, primitive_type_id):
        return primitive_type_id in self.enumerations_by_id

    def is_structured_data_type(self, primitive_type_id):
        return primitive_type_id in self.structures_data_types_by_id

    @staticmethod
    def serializer_for(enum_class: Type, enumeration):
        def serializer(value: Enum):
            literal_name = value.name
            for literal in enumeration.get_literals():
                if literal.get_name() == literal_name:
                    return literal.get_key()
            raise ValueError(f"Cannot serialize enum instance with name {literal_name}")

        return serializer

    @staticmethod
    def deserializer_for(enum_class: type[Enum], enumeration):
        def deserializer(serialized_value: str, required: bool):
            for literal in enumeration.get_literals():
                if literal.get_key() == serialized_value:
                    return enum_class[literal.get_name()]
            raise ValueError(f"Cannot deserialize value {serialized_value}")

        return deserializer

    def register_enum_class(self, enum_class: type, enumeration: Enumeration) -> None:
        id = enumeration.id
        if id is None:
            raise ValueError()
        self.primitive_serializers[id] = PrimitiveValuesSerialization.serializer_for(
            enum_class, enumeration
        )
        self.primitive_deserializers[id] = (
            PrimitiveValuesSerialization.deserializer_for(enum_class, enumeration)
        )

    def register_lion_builtins_primitive_serializers_and_deserializers(
        self, lion_web_version: LionWebVersion
    ) -> None:
        if lion_web_version is None:
            raise ValueError("lion_web_version should not be null")

        self.primitive_deserializers[
            cast(str, LionCoreBuiltins.get_boolean(lion_web_version).id)
        ] = lambda s, r: (None if not r and s is None else s.lower() == "true")
        self.primitive_deserializers[
            cast(str, LionCoreBuiltins.get_string(lion_web_version).id)
        ] = lambda s, r: s
        if lion_web_version == LionWebVersion.V2023_1:
            self.primitive_deserializers[
                cast(str, LionCoreBuiltins.get_json(lion_web_version).id)
            ] = lambda s, r: (None if s is None else json.loads(s))
        self.primitive_deserializers[
            cast(str, LionCoreBuiltins.get_integer(lion_web_version).id)
        ] = lambda s, r: (None if s is None else int(s))

        self.primitive_serializers[
            cast(str, LionCoreBuiltins.get_boolean(lion_web_version).id)
        ] = lambda v: str(v).lower()
        if lion_web_version == LionWebVersion.V2023_1:
            self.primitive_serializers[
                cast(str, LionCoreBuiltins.get_json(lion_web_version).id)
            ] = lambda v: json.dumps(v)
        self.primitive_serializers[
            cast(str, LionCoreBuiltins.get_string(lion_web_version).id)
        ] = lambda v: v
        self.primitive_serializers[
            cast(str, LionCoreBuiltins.get_integer(lion_web_version).id)
        ] = lambda v: str(v)
