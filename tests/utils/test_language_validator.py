import unittest

from lionwebpython.language import Annotation, Concept, Interface, Language
from lionwebpython.language.primitive_type import PrimitiveType
from lionwebpython.utils.language_validator import LanguageValidator


class LanguageValidatorTest(unittest.TestCase):

    def test_an_empty_annotation_is_invalid(self):
        language = Language("MyLanguageName", "mm-id", "mm-key")
        annotation = Annotation(key="aa-key", id="aa-id")
        language.add_element(annotation)
        result = LanguageValidator().validate(language)
        self.assertFalse(result.is_successful())

    def test_an_annotation_must_specify_annotated(self):
        language = Language("MyLanguage", "myM3ID", "myM3key")
        annotation = Annotation(
            language=language,
            name="MyAnnotation",
            key="annotation-key",
            id="annotation-id",
        )
        language.add_element(annotation)
        result = LanguageValidator().validate(language)
        self.assertFalse(result.is_successful())

    def test_an_annotation_can_be_valid(self):
        language = Language("MyLanguage", "myM3ID", "myM3key")
        annotation = Annotation(
            language=language,
            name="MyAnnotation",
            key="annotation-key",
            id="annotation-id",
        )
        c = Concept(language=language, name="C", id="c-id", key="c-key")
        annotation.set_annotates(c)
        language.add_element(annotation)
        result = LanguageValidator().validate(language)
        self.assertTrue(result.is_successful())

    def test_an_empty_primitive_type_is_invalid(self):
        language = Language("MyLanguage", "myM3ID", "myM3key")
        primitive_type = PrimitiveType(
            language=language, name="", id="pt-id", key="pt-key"
        )
        language.add_element(primitive_type)
        result = LanguageValidator().validate(language)
        self.assertFalse(result.is_successful())

    def test_a_primitive_type_can_be_valid(self):
        language = Language("MyLanguage", "myM3ID", "myM3key")
        primitive_type = PrimitiveType(
            language=language, name="PrimitiveType", id="pt-id", key="pt-key"
        )
        language.add_element(primitive_type)
        result = LanguageValidator().validate(language)
        self.assertTrue(result.is_successful())

    def test_simple_self_inheritance_is_caught(self):
        language = Language("MyLanguage", "myM3ID", "myM3key")
        concept = Concept(language=language, name="a", id="id-a", key="key-a")
        concept.set_extended_concept(concept)
        language.add_element(concept)
        result = LanguageValidator().validate(language)
        self.assertFalse(result.is_successful())

    def test_direct_self_inheritance_of_interfaces_is_caught(self):
        language = Language("MyLanguage", "myM3ID", "myM3key")
        interface = Interface(language=language, name="a", id="a-id", key="a-key")
        interface.add_extended_interface(interface)
        result = LanguageValidator().validate(language)
        self.assertFalse(result.is_successful())


if __name__ == "__main__":
    unittest.main()
