import unittest

from lionwebpython.language.concept import Concept
from lionwebpython.language.interface import Interface
from lionwebpython.language.language import Language
from lionwebpython.language.property import Property


class ConceptTest(unittest.TestCase):

    def test_a_concept_is_non_abstract_by_default(self):
        c = Concept()
        self.assertEqual(False, c.is_abstract())

    def test_features_and_inheritance_cycles(self):
        lang = Language(name="MyLanguage", id="l-id", key="l-key", version="123")
        a = Concept(language=lang, name="A", id="a-id", key="a-key")
        b = Concept(language=lang, name="B", id="b-id", key="b-key")
        c = Concept(language=lang, name="C", id="c-id", key="c-key")
        a.set_extended_concept(c)
        b.set_extended_concept(a)
        c.set_extended_concept(b)
        b.add_feature(Property(name="P1", container=b, id="p1-id").set_key("p1-key"))

        self.assertEqual(1, len(a.all_features()))
        self.assertEqual(1, len(a.inherited_features()))
        self.assertEqual(1, len(b.all_features()))
        self.assertEqual(1, len(b.inherited_features()))
        self.assertEqual(1, len(c.all_features()))
        self.assertEqual(1, len(c.inherited_features()))

    def test_check_duplicate_inheritance(self):
        lang = Language(name="MyLanguage", id="l-id", key="l-key", version="123")
        a = Interface(language=lang, name="A", id="a-id", key="a-key")
        b = Interface(language=lang, name="B", id="b-id", key="b-key")
        c = Interface(language=lang, name="C", id="c-id", key="c-key")
        d = Interface(language=lang, name="D", id="d-id", key="d-key")
        b.add_extended_interface(d)
        c.add_extended_interface(d)
        a.add_extended_interface(b)
        a.add_extended_interface(c)
        d.add_feature(Property(name="P1", container=d, id="p1-id").set_key("p1-key"))

        self.assertEqual(1, len(a.all_features()))
        self.assertEqual(1, len(a.inherited_features()))
        self.assertEqual(1, len(b.all_features()))
        self.assertEqual(1, len(b.inherited_features()))
        self.assertEqual(1, len(c.all_features()))
        self.assertEqual(1, len(c.inherited_features()))
        self.assertEqual(1, len(d.all_features()))
        self.assertEqual(0, len(d.inherited_features()))


if __name__ == "__main__":
    unittest.main()
