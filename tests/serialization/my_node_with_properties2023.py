from typing import Optional

from lionweb.language.concept import Concept
from lionweb.language.language import Language
from lionweb.language.lioncore_builtins import LionCoreBuiltins
from lionweb.language.property import Property
from lionweb.lionweb_version import LionWebVersion
from lionweb.model.classifier_instance_utils import (
    get_property_value_by_name, set_property_value_by_name)
from lionweb.model.impl.dynamic_node import DynamicNode


class MyNodeWithProperties2023(DynamicNode):
    LANGUAGE = (
        Language(lion_web_version=LionWebVersion.V2023_1)
        .set_id("mm1")
        .set_key("mylanguage")
        .set_name("MM1")
        .set_version("1")
    )

    CONCEPT: Concept = (
        Concept(lion_web_version=LionWebVersion.V2023_1)
        .set_id("concept-MyNodeWithProperties")
        .set_key("concept-MyNodeWithProperties")
        .set_name("MyNodeWithProperties")
        .add_feature(
            Property.create_optional(
                lion_web_version=LionWebVersion.V2023_1,
                name="p1",
                type=LionCoreBuiltins.get_boolean(LionWebVersion.V2023_1),
            )
            .set_id("p1")
            .set_key("p1")
        )
        .add_feature(
            Property.create_optional(
                lion_web_version=LionWebVersion.V2023_1,
                name="p2",
                type=LionCoreBuiltins.get_integer(LionWebVersion.V2023_1),
            )
            .set_id("p2")
            .set_key("p2")
        )
        .add_feature(
            Property.create_optional(
                lionweb_version=LionWebVersion.V2023_1,
                name="p3",
                type=LionCoreBuiltins.get_string(LionWebVersion.V2023_1),
            )
            .set_id("p3")
            .set_key("p3")
        )
        .add_feature(
            Property.create_optional(
                lionweb_version=LionWebVersion.V2023_1,
                name="p4",
                type=LionCoreBuiltins.get_json(LionWebVersion.V2023_1),
            )
            .set_id("p4")
            .set_key("p4")
        )
        .set_parent(LANGUAGE)
    )

    LANGUAGE.add_element(CONCEPT)

    def __init__(self, id: str):
        super().__init__(id, MyNodeWithProperties2023.CONCEPT)

    def get_p1(self) -> Optional[bool]:
        return get_property_value_by_name(self, "p1")

    def get_p2(self) -> Optional[int]:
        return get_property_value_by_name(self, "p2")

    def get_p3(self) -> Optional[str]:
        return get_property_value_by_name(self, "p3")

    def get_p4(self) -> Optional[dict]:
        p4_value = get_property_value_by_name(self, "p4")
        return p4_value

    def set_p1(self, value: bool):
        set_property_value_by_name(self, "p1", value)

    def set_p2(self, value: int):
        set_property_value_by_name(self, "p2", value)

    def set_p3(self, value: str):
        set_property_value_by_name(self, "p3", value)

    def set_p4(self, value: dict):
        set_property_value_by_name(self, "p4", value)
