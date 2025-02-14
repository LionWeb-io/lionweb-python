from lionwebpython.language.concept import Concept
from lionwebpython.language.language import Language
from lionwebpython.language.lioncore_builtins import LionCoreBuiltins
from lionwebpython.language.property import Property
from lionwebpython.model.classifier_instance_utils import \
    ClassifierInstanceUtils
from lionwebpython.model.impl.dynamic_node import DynamicNode


class MyNodeWithProperties(DynamicNode):
    LANGUAGE = (
        Language().set_id("mm1").set_key("mylanguage").set_name("MM1").set_version("1")
    )

    CONCEPT = (
        Concept()
        .set_id("concept-MyNodeWithProperties")
        .set_key("concept-MyNodeWithProperties")
        .set_name("MyNodeWithProperties")
        .add_feature(
            Property.create_optional(name="p1", type=LionCoreBuiltins.get_boolean())
            .set_id("p1")
            .set_key("p1")
        )
        .add_feature(
            Property.create_optional(name="p2", type=LionCoreBuiltins.get_integer())
            .set_id("p2")
            .set_key("p2")
        )
        .add_feature(
            Property.create_optional(name="p3", type=LionCoreBuiltins.get_string())
            .set_id("p3")
            .set_key("p3")
        )
        .set_parent(LANGUAGE)
    )

    LANGUAGE.add_element(CONCEPT)

    def __init__(self, id):
        super().__init__(id, MyNodeWithProperties.CONCEPT)

    def get_p1(self):
        return ClassifierInstanceUtils.get_property_value_by_name(self, "p1")

    def get_p2(self):
        return ClassifierInstanceUtils.get_property_value_by_name(self, "p2")

    def get_p3(self):
        return ClassifierInstanceUtils.get_property_value_by_name(self, "p3")

    def get_p4(self):
        return ClassifierInstanceUtils.get_property_value_by_name(self, "p4")

    def set_p1(self, value: bool):
        ClassifierInstanceUtils.set_property_value_by_name(self, "p1", value)

    def set_p2(self, value: int):
        ClassifierInstanceUtils.set_property_value_by_name(self, "p2", value)

    def set_p3(self, value: str):
        ClassifierInstanceUtils.set_property_value_by_name(self, "p3", value)

    def set_p4(self, value):
        ClassifierInstanceUtils.set_property_value_by_name(self, "p4", value)
