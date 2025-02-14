import unittest

from lionwebpython.language.concept import Concept
from lionwebpython.language.interface import Interface
from lionwebpython.language.language import Language
from lionwebpython.model.classifier_instance_utils import \
    ClassifierInstanceUtils
from lionwebpython.model.reference_value import ReferenceValue
from lionwebpython.self.lioncore import LionCore


class ConceptReflectionTest(unittest.TestCase):

    def test_get_property_value_name(self):
        language = Language()
        concept = Concept(language=language, name="MyConcept")
        prop = LionCore.get_concept().get_property_by_name("name")
        self.assertIsNotNone(prop)
        self.assertEqual(
            "MyConcept",
            concept.get_property_value(property=prop),
        )

    def test_set_property_value_name(self):
        language = Language()
        concept = Concept(language=language, name="MyConcept")
        concept.set_property_value(
            property=LionCore.get_concept().get_property_by_name("name"),
            value="MyAmazingConcept",
        )
        self.assertEqual("MyAmazingConcept", concept.get_name())

    def test_get_property_value_abstract(self):
        language = Language()
        concept = Concept(language=language, name="MyConcept")
        property_ = LionCore.get_concept().get_property_by_name("abstract")
        concept.set_abstract(True)
        self.assertEqual(True, concept.get_property_value(property=property_))
        concept.set_abstract(False)
        self.assertEqual(False, concept.get_property_value(property=property_))

    def test_set_property_value_abstract(self):
        language = Language()
        concept = Concept(language=language, name="MyConcept")
        property_ = LionCore.get_concept().get_property_by_name("abstract")
        concept.set_property_value(property=property_, value=True)
        self.assertTrue(concept.is_abstract())
        concept.set_property_value(property=property_, value=False)
        self.assertFalse(concept.is_abstract())

    def test_get_reference_extended(self):
        language = Language()
        concept = Concept(language=language, name="MyConcept")
        other_concept = Concept(language=language, name="OtherConcept")
        reference = LionCore.get_concept().get_reference_by_name("extends")
        concept.set_extended_concept(None)
        self.assertEqual(
            [], ClassifierInstanceUtils.get_referred_nodes(concept, reference)
        )
        concept.set_extended_concept(other_concept)
        self.assertEqual(
            [other_concept],
            ClassifierInstanceUtils.get_referred_nodes(concept, reference),
        )

    def test_set_reference_extended(self):
        language = Language()
        concept = Concept(language=language, name="MyConcept")
        other_concept = Concept(language=language, name="OtherConcept")
        reference = LionCore.get_concept().get_reference_by_name("extends")
        self.assertIsNotNone(reference)
        concept.add_reference_value(reference, None)
        self.assertIsNone(concept.get_extended_concept())
        concept.add_reference_value(reference, ReferenceValue(other_concept, None))
        self.assertEqual(other_concept, concept.get_extended_concept())

    def test_get_reference_implemented(self):
        language = Language()
        concept = Concept(language=language, name="MyConcept")
        i1 = Interface(language=language, name="I1")
        i2 = Interface(language=language, name="I2")
        reference = LionCore.get_concept().get_reference_by_name("implements")
        self.assertEqual(
            [], ClassifierInstanceUtils.get_referred_nodes(concept, reference)
        )
        concept.add_implemented_interface(i1)
        self.assertEqual(
            [i1], ClassifierInstanceUtils.get_referred_nodes(concept, reference)
        )
        concept.add_implemented_interface(i2)
        self.assertEqual(
            [i1, i2], ClassifierInstanceUtils.get_referred_nodes(concept, reference)
        )

    def test_set_reference_implemented(self):
        language = Language()
        concept = Concept(language=language, name="MyConcept")
        i1 = Interface(language=language, name="I1")
        i2 = Interface(language=language, name="I2")
        reference = LionCore.get_concept().get_reference_by_name("implements")
        self.assertEqual([], concept.get_implemented())
        concept.add_reference_value(reference, ReferenceValue(i1, None))
        self.assertEqual([i1], concept.get_implemented())
        concept.add_reference_value(reference, ReferenceValue(i2, None))
        self.assertEqual([i1, i2], concept.get_implemented())


if __name__ == "__main__":
    unittest.main()
