import unittest

from lionwebpython.language.concept import Concept
from lionwebpython.language.interface import Interface
from lionwebpython.language.language import Language


class SimpleLanguageLanguageTest(unittest.TestCase):

    def test_empty_language_definition(self):
        language = Language("SimpleLanguage")
        language.set_id("myM3ID")
        self.assertEqual("SimpleLanguage", language.get_name())
        self.assertEqual("SimpleLanguage", language.namespace_qualifier())
        self.assertEqual(0, len(language.depends_on()))
        self.assertEqual(0, len(language.get_elements()))

    def test_empty_concept_definition(self):
        language = Language("SimpleLanguage")
        language.set_id("myM3ID")
        expression = Concept(language=language, name="Expression")
        self.assertEqual("Expression", expression.get_name())
        self.assertIs(language, expression.get_container())
        self.assertIs(language, expression.get_language())
        self.assertEqual("SimpleLanguage.Expression", expression.qualified_name())
        self.assertEqual("SimpleLanguage.Expression", expression.namespace_qualifier())
        self.assertIsNone(expression.get_extended_concept())
        self.assertEqual(0, len(expression.get_implemented()))
        self.assertEqual(0, len(expression.get_features()))
        self.assertFalse(expression.is_abstract())

    def test_empty_interface_definition(self):
        language = Language(name="SimpleLanguage")
        language.set_id("myM3ID")
        deprecated = Interface(language=language, name="Deprecated")
        self.assertEqual("Deprecated", deprecated.get_name())
        self.assertIs(language, deprecated.get_container())
        self.assertIs(language, deprecated.get_language())
        self.assertEqual("SimpleLanguage.Deprecated", deprecated.qualified_name())
        self.assertEqual("SimpleLanguage.Deprecated", deprecated.namespace_qualifier())
        self.assertEqual(0, len(deprecated.get_extended_interfaces()))
        self.assertEqual(0, len(deprecated.get_features()))


if __name__ == "__main__":
    unittest.main()
