import unittest

from serialization.my_annotation import MyAnnotation

from lionweb.model.classifier_instance_utils import (
    get_property_value_by_name, set_property_value_by_name)
from lionweb.model.impl.dynamic_node import DynamicNode


class TestDynamicAnnotation(unittest.TestCase):

    def test_annotation_with_children(self):
        my_annotation = MyAnnotation(id="ann1")
        value1 = DynamicNode("value1", MyAnnotation.VALUE)

        set_property_value_by_name(value1, "amount", 123)
        my_annotation.add_child(containment="values", child=value1)

        self.assertEqual(1, len(my_annotation.get_children("values")))

        retrieved_value1 = my_annotation.get_children("values")[0]
        self.assertEqual(
            123,
            get_property_value_by_name(retrieved_value1, "amount"),
        )


if __name__ == "__main__":
    unittest.main()
