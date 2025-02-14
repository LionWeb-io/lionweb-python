import unittest

from lionwebpython.language.annotation import Annotation
from lionwebpython.language.concept import Concept
from lionwebpython.language.containment import Containment
from lionwebpython.language.enumeration import Enumeration
from lionwebpython.language.enumeration_literal import EnumerationLiteral
from lionwebpython.language.interface import Interface
from lionwebpython.language.language import Language
from lionwebpython.language.primitive_type import PrimitiveType
from lionwebpython.language.property import Property
from lionwebpython.language.reference import Reference
from lionwebpython.self.lioncore import LionCore


class MetaCircularityTest(unittest.TestCase):

    def test_each_element_of_m3_has_right_concept(self):
        self.assertIs(LionCore.get_concept(), LionCore.get_concept().get_classifier())
        self.assertIs(LionCore.get_concept(), LionCore.get_interface().get_classifier())
        self.assertIs(
            LionCore.get_concept(), LionCore.get_containment().get_classifier()
        )
        self.assertIs(LionCore.get_concept(), LionCore.get_data_type().get_classifier())
        self.assertIs(
            LionCore.get_concept(), LionCore.get_enumeration().get_classifier()
        )
        self.assertIs(
            LionCore.get_concept(), LionCore.get_enumeration_literal().get_classifier()
        )
        self.assertIs(LionCore.get_concept(), LionCore.get_feature().get_classifier())
        self.assertIs(
            LionCore.get_concept(), LionCore.get_classifier().get_classifier()
        )
        self.assertIs(LionCore.get_concept(), LionCore.get_link().get_classifier())
        self.assertIs(LionCore.get_concept(), LionCore.get_language().get_classifier())
        self.assertIs(
            LionCore.get_concept(), LionCore.get_language_entity().get_classifier()
        )
        self.assertIs(
            LionCore.get_concept(), LionCore.get_primitive_type().get_classifier()
        )
        self.assertIs(LionCore.get_concept(), LionCore.get_property().get_classifier())
        self.assertIs(LionCore.get_concept(), LionCore.get_reference().get_classifier())
        self.assertIs(
            LionCore.get_concept(), LionCore.get_annotation().get_classifier()
        )

    def test_each_element_of_m2_has_right_concept(self):
        self.assertIs(LionCore.get_concept(), Concept().get_classifier())
        self.assertIs(LionCore.get_interface(), Interface().get_classifier())
        self.assertIs(LionCore.get_containment(), Containment().get_classifier())
        self.assertIs(LionCore.get_enumeration(), Enumeration().get_classifier())
        self.assertIs(
            LionCore.get_enumeration_literal(), EnumerationLiteral().get_classifier()
        )
        self.assertIs(LionCore.get_language(), Language().get_classifier())
        self.assertIs(LionCore.get_primitive_type(), PrimitiveType().get_classifier())
        self.assertIs(LionCore.get_property(), Property().get_classifier())
        self.assertIs(LionCore.get_reference(), Reference().get_classifier())
        self.assertIs(LionCore.get_annotation(), Annotation().get_classifier())


if __name__ == "__main__":
    unittest.main()
