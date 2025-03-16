import unittest

from serialization.my_node_with_properties import MyNodeWithProperties
from serialization.my_node_with_properties2023 import MyNodeWithProperties2023

from lionwebpython.language.concept import Concept
from lionwebpython.language.containment import Containment
from lionwebpython.language.language import Language
from lionwebpython.language.lioncore_builtins import LionCoreBuiltins
from lionwebpython.language.property import Property
from lionwebpython.model.classifier_instance_utils import \
    ClassifierInstanceUtils
from lionwebpython.model.impl.dynamic_node import DynamicNode


class DynamicNodeTest(unittest.TestCase):

    def test_equality_positive_case_empty_nodes(self):
        n1 = MyNodeWithProperties("id1")
        n2 = MyNodeWithProperties("id1")
        self.assertEqual(n1, n2)

    def test_equality_negative_case_empty_nodes(self):
        n1 = MyNodeWithProperties("id1")
        n2 = MyNodeWithProperties("id2")
        self.assertNotEqual(n1, n2)

    def test_equality_positive_case_with_properties(self):
        n1 = MyNodeWithProperties2023("id1")
        n1.set_p1(True)
        n1.set_p2(123)
        n1.set_p3("foo")
        n1.set_p4([])
        n2 = MyNodeWithProperties2023("id1")
        n2.set_p1(True)
        n2.set_p2(123)
        n2.set_p3("foo")
        n2.set_p4([])
        self.assertEqual(n1, n2)

    def test_equality_negative_case_with_properties(self):
        n1 = MyNodeWithProperties2023("id1")
        n1.set_p1(True)
        n1.set_p2(123)
        n1.set_p3("foo")
        n1.set_p4([])
        n2 = MyNodeWithProperties2023("id1")
        n2.set_p1(True)
        n2.set_p2(123)
        n2.set_p3("bar")
        n2.set_p4([])
        self.assertNotEqual(n1, n2)

    def test_remove_child_on_single_containment(self):
        c = Concept()
        containment = Containment.create_optional("ch", c)
        containment.set_key("my-containment")
        c.add_feature(containment)
        n1 = DynamicNode("id-123", c)
        n2 = DynamicNode("id-456", c)

        self.assertEqual([], n1.get_children(containment))
        n1.add_child(containment, n2)
        self.assertEqual([n2], n1.get_children(containment))
        n1.remove_child(child=n2)
        self.assertEqual([], n1.get_children(containment))

    def test_remove_child_on_multiple_containment(self):
        c = Concept()
        containment = Containment.create_multiple("ch", c)
        containment.set_key("my-containment")
        c.add_feature(containment)
        n1 = DynamicNode("id-123", c)
        n2 = DynamicNode("id-456", c)
        n3 = DynamicNode("id-789", c)
        n4 = DynamicNode("id-012", c)

        self.assertEqual([], n1.get_children(containment))
        n1.add_child(containment, n2)
        n1.add_child(containment, n3)
        n1.add_child(containment, n4)
        self.assertEqual([n2, n3, n4], n1.get_children(containment))
        n1.remove_child(child=n3)
        self.assertEqual([n2, n4], n1.get_children(containment))
        n1.remove_child(child=n2)
        self.assertEqual([n4], n1.get_children(containment))
        n1.remove_child(child=n4)
        self.assertEqual([], n1.get_children(containment))

    def test_get_root_simple_cases(self):
        lang = Language("MyLanguage", "l-id", "l-key", "123")
        a = Concept(language=lang, name="A", id="a-id", key="a-key")
        n1 = DynamicNode("n1", a)
        n2 = DynamicNode("n2", a)
        n3 = DynamicNode("n3", a)
        n4 = DynamicNode("n4", a)

        n2.set_parent(n1)
        n3.set_parent(n2)
        n4.set_parent(n3)

        self.assertEqual(n1, n1.get_root())
        self.assertEqual(n1, n2.get_root())
        self.assertEqual(n1, n3.get_root())
        self.assertEqual(n1, n4.get_root())

    def test_get_root_circular_hierarchy(self):
        lang = Language("MyLanguage", "l-id", "l-key", "123")
        a = Concept(language=lang, name="A", id="a-id", key="a-key")
        n1 = DynamicNode("n1", a)
        n2 = DynamicNode("n2", a)
        n3 = DynamicNode("n3", a)
        n4 = DynamicNode("n4", a)

        n1.set_parent(n4)
        n2.set_parent(n1)
        n3.set_parent(n2)
        n4.set_parent(n3)

        with self.assertRaises(RuntimeError):
            n1.get_root()
        with self.assertRaises(RuntimeError):
            n2.get_root()
        with self.assertRaises(RuntimeError):
            n3.get_root()
        with self.assertRaises(RuntimeError):
            n4.get_root()

    def test_setting_true_non_nullable_boolean_property(self):
        lang = Language("MyLanguage", "l-id", "l-key", "123")
        a = Concept(language=lang, name="A", id="a-id", key="a-key")
        a.add_feature(
            Property.create_required(name="foo", type=LionCoreBuiltins.get_boolean())
            .set_id("foo-id")
            .set_key("foo-key")
        )
        n1 = DynamicNode("n1", a)

        self.assertEqual(
            False, ClassifierInstanceUtils.get_property_value_by_name(n1, "foo")
        )
        ClassifierInstanceUtils.set_property_value_by_name(n1, "foo", True)
        self.assertEqual(
            True, ClassifierInstanceUtils.get_property_value_by_name(n1, "foo")
        )

    def test_setting_false_nullable_boolean_property(self):
        lang = Language("MyLanguage", "l-id", "l-key", "123")
        a = Concept(language=lang, name="A", id="a-id", key="a-key")
        a.add_feature(
            Property.create_optional(name="foo", type=LionCoreBuiltins.get_boolean())
            .set_id("foo-id")
            .set_key("foo-key")
        )
        n1 = DynamicNode("n1", a)

        self.assertIsNone(ClassifierInstanceUtils.get_property_value_by_name(n1, "foo"))
        ClassifierInstanceUtils.set_property_value_by_name(n1, "foo", False)
        self.assertEqual(
            False, ClassifierInstanceUtils.get_property_value_by_name(n1, "foo")
        )

    def test_setting_null_nullable_boolean_property(self):
        lang = Language("MyLanguage", "l-id", "l-key", "123")
        a = Concept(language=lang, name="A", id="a-id", key="a-key")
        a.add_feature(
            Property.create_optional(name="foo", type=LionCoreBuiltins.get_boolean())
            .set_id("foo-id")
            .set_key("foo-key")
        )
        n1 = DynamicNode("n1", a)

        self.assertIsNone(ClassifierInstanceUtils.get_property_value_by_name(n1, "foo"))
        ClassifierInstanceUtils.set_property_value_by_name(n1, "foo", None)
        self.assertIsNone(ClassifierInstanceUtils.get_property_value_by_name(n1, "foo"))

        # Check also what happens when we null a value that was previously not null
        ClassifierInstanceUtils.set_property_value_by_name(n1, "foo", True)
        self.assertEqual(
            True, ClassifierInstanceUtils.get_property_value_by_name(n1, "foo")
        )

        ClassifierInstanceUtils.set_property_value_by_name(n1, "foo", None)
        self.assertIsNone(ClassifierInstanceUtils.get_property_value_by_name(n1, "foo"))


if __name__ == "__main__":
    unittest.main()
