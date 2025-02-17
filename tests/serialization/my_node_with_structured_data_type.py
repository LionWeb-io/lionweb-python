from typing import Optional, cast

from lionwebpython.language import Concept, Language, Property
from lionwebpython.language.field import Field
from lionwebpython.language.lioncore_builtins import LionCoreBuiltins
from lionwebpython.language.structured_data_type import StructuredDataType
from lionwebpython.model.impl.dynamic_node import DynamicNode


class MyNodeWithStructuredDataType(DynamicNode):
    LANGUAGE = Language(id="mm3", key="mylanguageWithSDT", name="MMSDT", version="1")

    CONCEPT = Concept(
        id="concept-MyNodeWithStructuredDataType",
        key="concept-MyNodeWithStructuredDataType",
        name="MyNodeWithStructuredDataType",
        language=LANGUAGE,
    )

    POINT = (
        StructuredDataType(
            id="point-id", key="point-key", name="point", language=LANGUAGE
        )
        .add_field(Field("x", LionCoreBuiltins.get_integer(), "x-id", "x-key"))
        .add_field(Field("y", LionCoreBuiltins.get_integer(), "y-id", "y-key"))
    )

    ADDRESS = (
        StructuredDataType(
            id="address-id", key="address-key", name="address", language=LANGUAGE
        )
        .add_field(
            Field("street", LionCoreBuiltins.get_string(), "street-id", "street-key")
        )
        .add_field(Field("city", LionCoreBuiltins.get_string(), "city-id", "city-key"))
    )

    CONCEPT.add_feature(Property.create_required(name="point", type=POINT))
    CONCEPT.add_feature(Property.create_optional(name="address", type=ADDRESS))
    LANGUAGE.add_element(CONCEPT)
    LANGUAGE.add_element(POINT)
    LANGUAGE.add_element(ADDRESS)

    def __init__(self, id: str):
        super().__init__(id, MyNodeWithStructuredDataType.CONCEPT)

    def get_point(self) -> Optional[StructuredDataType]:
        return cast(
            Optional[StructuredDataType], self.get_property_value(property_name="point")
        )

    def set_point(self, point: StructuredDataType) -> None:
        self.set_property_value(property_name="point", value=point)

    def get_address(self) -> Optional[StructuredDataType]:
        return cast(
            Optional[StructuredDataType],
            self.get_property_value(property_name="address"),
        )

    def set_address(self, address: StructuredDataType) -> None:
        self.set_property_value(property_name="address", value=address)
