import unittest

from lionwebpython.language import (Annotation, Concept, Containment,
                                    Interface, Language, Property)
from lionwebpython.model.classifier_instance_utils import \
    ClassifierInstanceUtils
from lionwebpython.model.reference_value import ReferenceValue
from lionwebpython.self.lioncore import LionCore

from .base_test import BaseTest


class AnnotationTest(BaseTest):

    def test_get_property_value_name(self):
        language = Language()
        annotation = Annotation(language=language, name="MyAnnotation")
        name_prop = LionCore.get_annotation().get_property_by_name("name")
        self.assertIsNotNone(name_prop)
        self.assertEqual(
            "MyAnnotation", annotation.get_property_value(property=name_prop)
        )

    def test_set_property_value_name(self):
        language = Language()
        annotation = Annotation(language=language, name="MyAnnotation")
        annotation.set_property_value(
            property=LionCore.get_annotation().get_property_by_name("name"),
            value="MyAmazingAnnotation",
        )
        self.assertEqual("MyAmazingAnnotation", annotation.get_name())

    def test_get_reference_value_target(self):
        language = Language("mymm")
        annotation = Annotation(language=language, name="MyAnnotation")
        self.assertEqual(
            [],
            ClassifierInstanceUtils.get_referred_nodes(
                annotation, LionCore.get_annotation().get_reference_by_name("annotates")
            ),
        )

        my_concept = Concept(language=language, name="myc")
        annotation.set_annotates(my_concept)
        self.assertEqual(
            [my_concept],
            ClassifierInstanceUtils.get_referred_nodes(
                annotation, LionCore.get_annotation().get_reference_by_name("annotates")
            ),
        )

    def test_set_reference_value_target(self):
        language = Language()
        annotation = Annotation(language=language, name="MyAnnotation")

        my_concept = Concept()
        annotation.add_reference_value(
            LionCore.get_annotation().get_reference_by_name("annotates"),
            ReferenceValue(my_concept, None),
        )
        self.assertEqual(my_concept, annotation.get_annotates())

    def test_get_property_value_features(self):
        language = Language()
        annotation = Annotation(language=language, name="MyAnnotation")
        self.assertEqual(
            [],
            annotation.get_children(
                LionCore.get_annotation().get_containment_by_name("features")
            ),
        )

        prop = Property()
        annotation.add_feature(prop)
        self.assertEqual(
            [prop],
            annotation.get_children(
                LionCore.get_annotation().get_containment_by_name("features")
            ),
        )

    def test_annotates(self):
        language = Language(name="LangFoo", id="lf", key="lf")
        my_concept = Concept(language=language, name="MyConcept", id="c", key="c")
        other_annotation = Annotation(
            language=language, name="OtherAnnotation", id="oa", key="oa"
        )
        other_annotation.set_annotates(my_concept)
        super_annotation = Annotation(
            language=language, name="SuperAnnotation", id="sa", key="sa"
        )
        super_annotation.set_annotates(my_concept)
        my_ci = Interface(language=language, name="MyCI", id="ci", key="ci")

        annotation = Annotation(
            language=language, name="MyAnnotation", id="MyAnnotation-ID", key="ma"
        )
        self.assertIsNone(annotation.get_annotates())
        self.assert_node_tree_is_valid(annotation)
        self.assert_language_is_not_valid(language)

        annotation.set_annotates(my_concept)
        self.assertEqual(my_concept, annotation.get_annotates())
        self.assert_node_tree_is_valid(annotation)
        self.assert_language_is_valid(language)

        annotation.set_annotates(my_ci)
        self.assertEqual(my_ci, annotation.get_annotates())
        self.assert_node_tree_is_valid(annotation)
        self.assert_language_is_valid(language)

        annotation.set_annotates(other_annotation)
        self.assertEqual(other_annotation, annotation.get_annotates())
        self.assert_node_tree_is_valid(annotation)
        self.assert_language_is_valid(language)

        annotation.set_annotates(None)
        self.assertIsNone(annotation.get_annotates())
        self.assert_node_tree_is_valid(annotation)
        self.assert_language_is_not_valid(language)

        annotation.set_extended_annotation(super_annotation)
        self.assertIsNone(annotation.get_annotates())
        self.assertEqual(my_concept, annotation.get_effectively_annotated())
        self.assert_node_tree_is_valid(annotation)
        self.assert_language_is_valid(language)

    def test_containment_links(self):
        language = Language("LangFoo", "lf", "lf")
        my_concept = Concept(language=language, name="MyConcept", id="c", key="c")

        annotation = Annotation(
            language=language, name="MyAnnotation", id="MyAnnotation-ID", key="ma"
        )
        annotation.set_annotates(my_concept)
        self.assert_node_tree_is_valid(annotation)
        self.assert_language_is_valid(language)

        annotation.add_feature(
            Containment.create_optional("cont", my_concept, "cont", "cont-key")
        )
        self.assert_node_tree_is_valid(annotation)
        self.assert_language_is_valid(language)


if __name__ == "__main__":
    unittest.main()
